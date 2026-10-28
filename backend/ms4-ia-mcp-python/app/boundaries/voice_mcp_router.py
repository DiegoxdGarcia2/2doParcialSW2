"""
=============================================================================
 AegisCore AI - MS4: Router de API para Servidor MCP y Reportes por Voz
 Caso de Uso 15 (CU15) — ICONIX: Estereotipo Boundary
 Expone:
   - POST /api/v1/mcp/voice-command (Multipart Audio / JSON prompt)
   - GET  /api/v1/mcp/tools (Catálogo oficial de herramientas MCP)
   - POST /api/v1/mcp/execute-tool (Ejecución directa tipada)
   - GET  /api/v1/mcp/download-report/{filename} (Descarga HTTP Streaming)
=============================================================================
"""

import os
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Query
from fastapi.responses import FileResponse

from app.entities.voice_mcp_dto import (
    VoiceCommandRequest,
    VoiceMcpExecutionResponse,
    McpToolDefinitionDTO
)
from app.controls.voice_mcp_control import VoiceMcpControl

router = APIRouter(prefix="/api/v1/mcp", tags=["CU15 - Voice MCP Reports & Anti-SQLi"])
control = VoiceMcpControl()

REPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "artifacts" / "reports"


@router.get("/tools", response_model=List[McpToolDefinitionDTO], summary="Catálogo Oficial de Herramientas MCP")
async def listar_herramientas_mcp():
    """Retorna las 4 herramientas oficiales del servidor MCP con sus esquemas JSON Schema."""
    return control.obtenerCatalogoTools()


@router.post("/voice-command", response_model=VoiceMcpExecutionResponse, summary="Procesar Comando de Voz con Whisper y MCP")
async def procesar_comando_voz(
    audio_file: Optional[UploadFile] = File(default=None, description="Archivo de audio binario desde micrófono (.wav, .webm, .mp3)"),
    prompt_dictado: Optional[str] = Form(default=None, description="Texto dictado opcional (vía Web Speech API o prompt directo)"),
    formato_preferido: str = Form(default="pdf", description="Formato preferido: xlsx, pdf o docx"),
    herramienta_sugerida: Optional[str] = Form(default=None, description="Herramienta MCP específica (opcional)")
):
    """
    Endpoint principal de voz para Angular MF1 y Flutter:
    1. Si se envía archivo de audio, lo decodifica acústicamente vía Whisper STT.
    2. Pasa por el filtro de seguridad OWASP Anti-SQLi.
    3. Si detecta inyección SQL, bloquea la consulta y retorna código de amenaza.
    4. Si es seguro, ejecuta la herramienta MCP con consultas parametrizadas.
    5. Retorna la respuesta completa con el enlace de descarga física del reporte.
    """
    audio_bytes = None
    if audio_file:
        audio_bytes = await audio_file.read()

    if not audio_bytes and not prompt_dictado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar un archivo de audio o un texto dictado en el parámetro 'prompt_dictado'."
        )

    response = control.procesarComandoVozCompleto(
        audio_bytes=audio_bytes,
        texto_dictado=prompt_dictado,
        formato_preferido=formato_preferido,
        herramienta_sugerida=herramienta_sugerida
    )

    # Si fue bloqueado por inyección SQL, retornamos HTTP 400 con la auditoría de amenaza
    if response.auditoria_seguridad.es_amenaza:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Ataque de Inyección SQL neutralizado por blindaje OWASP",
                "auditoria_seguridad": response.auditoria_seguridad.model_dump(),
                "mensaje": response.mensaje
            }
        )

    return response


@router.post("/voice-command/json", response_model=VoiceMcpExecutionResponse, summary="Procesar Comando en JSON Directo")
async def procesar_comando_json(request: VoiceCommandRequest):
    """Versión JSON del endpoint de comando para pruebas directas o clientes sin multipart."""
    if not request.prompt_dictado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo 'prompt_dictado' es requerido."
        )

    response = control.procesarComandoVozCompleto(
        audio_bytes=None,
        texto_dictado=request.prompt_dictado,
        formato_preferido=request.formato_preferido,
        herramienta_sugerida=request.herramienta_sugerida,
        parametros_manuales=request.parametros_manuales
    )

    if response.auditoria_seguridad.es_amenaza:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Ataque de Inyección SQL neutralizado por blindaje OWASP",
                "auditoria_seguridad": response.auditoria_seguridad.model_dump(),
                "mensaje": response.mensaje
            }
        )

    return response


@router.get("/download-report/{filename}", summary="Descargar Archivo Físico Compilado")
async def descargar_reporte(filename: str):
    """Permite descargar por HTTP streaming el archivo generado (.xlsx, .pdf o .docx)."""
    # Blindaje contra path traversal
    safe_filename = os.path.basename(filename)
    filepath = REPORTS_DIR / safe_filename

    if not filepath.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El archivo solicitado '{safe_filename}' no existe o ha expirado."
        )

    ext = safe_filename.split(".")[-1].lower()
    media_types = {
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(
        path=str(filepath),
        filename=safe_filename,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{safe_filename}"'}
    )
