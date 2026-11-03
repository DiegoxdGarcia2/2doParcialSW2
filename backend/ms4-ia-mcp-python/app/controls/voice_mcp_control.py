"""
=============================================================================
 AegisCore AI - MS4: Clase de Control ICONIX para Reportes por Voz con MCP
 Caso de Uso 15 (CU15) — ICONIX: Estereotipo Control
 Orquesta:
   1. WhisperSTTEngine: Transcripción acústica de audio (Modo A)
   2. OwaspAntiSqliGuard: Detección y bloqueo de inyecciones SQL
   3. McpProtocolServer: Ejecución tipada de herramientas MCP
   4. Exporters: Generación física de archivos .xlsx, .pdf, .docx
 Métodos operacionales con nombres explícitos para UML 2.5+.
=============================================================================
"""

import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from app.services.s3_storage_service import s3_storage_service

from app.entities.voice_mcp_dto import (
    OwaspSecurityAuditDTO,
    McpToolInvocationTraceDTO,
    GeneratedDocumentDTO,
    VoiceMcpExecutionResponse,
    McpToolDefinitionDTO
)
from app.mcp_voice_reports.stt.whisper_engine import WhisperSTTEngine
from app.mcp_voice_reports.security.owasp_antisqli_guard import OwaspAntiSqliGuard
from app.mcp_voice_reports.server.mcp_protocol_server import McpProtocolServer
from app.mcp_voice_reports.exporters.excel_exporter import ExcelDocumentExporter
from app.mcp_voice_reports.exporters.pdf_exporter import PdfDocumentExporter
from app.mcp_voice_reports.exporters.word_exporter import WordDocumentExporter


REPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "artifacts" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class VoiceMcpControl:
    """Clase de Control ICONIX que orquesta el pipeline de voz, MCP, seguridad y compilación documental."""

    def __init__(self):
        self.stt_engine = WhisperSTTEngine()
        self.security_guard = OwaspAntiSqliGuard()
        self.mcp_server = McpProtocolServer()

    def transcribirAudioWhisper(
        self,
        audio_bytes: Optional[bytes] = None,
        texto_dictado: Optional[str] = None,
        formato: Optional[str] = None
    ) -> Tuple[str, str, str, Dict[str, Any]]:
        """
        Operación UML 2.5+: transcribirAudioWhisper()
        Decodifica la trama acústica o toma el texto dictado en lenguaje natural.
        """
        return self.stt_engine.transcribir_audio(
            audio_bytes=audio_bytes,
            texto_fallback=texto_dictado,
            formato_default=formato
        )

    def auditarSeguridadAntiSQLi(self, texto: str) -> OwaspSecurityAuditDTO:
        """
        Operación UML 2.5+: auditarSeguridadAntiSQLi()
        Evalúa el texto dictado contra vectores de ataque de inyección SQL (OWASP A03:2021).
        """
        return self.security_guard.auditar_texto(texto)

    def ejecutarHerramientaMCP(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any], List[str], List[Dict[str, Any]], McpToolInvocationTraceDTO]:
        """
        Operación UML 2.5+: ejecutarHerramientaMCP()
        Invoca la herramienta MCP con consultas ORM parametrizadas a Neon PostgreSQL y MongoDB Atlas.
        """
        return self.mcp_server.call_tool(tool_name, arguments)

    def exportarReporteDocumento(
        self,
        titulo: str,
        kpis: Dict[str, Any],
        columnas: List[str],
        filas: List[Dict[str, Any]],
        formato: str = "pdf",
        nombre_base: str = "reporte_mcp",
        params: Optional[Dict[str, Any]] = None
    ) -> GeneratedDocumentDTO:
        """
        Operación UML 2.5+: exportarReporteDocumento()
        Compila el archivo descargable según el formato solicitado (.xlsx, .pdf o .docx).
        Aplica persistencia dual: guarda copia local en disco y sube a Amazon S3 con Pre-signed URL.
        """
        fmt = formato.lower().strip()
        if fmt == "xlsx":
            documento = ExcelDocumentExporter.generar_reporte(titulo, kpis, columnas, filas, nombre_base)
        elif fmt == "docx":
            documento = WordDocumentExporter.generar_reporte(titulo, kpis, columnas, filas, nombre_base)
        else:
            documento = PdfDocumentExporter.generar_reporte(titulo, kpis, columnas, filas, nombre_base)

        # Asignar ruta de descarga directa del microservicio local
        documento.local_download_url = f"/api/v1/mcp/download-report/{documento.filename}"

        # Subida dual a Amazon S3 si el servicio está configurado
        if s3_storage_service.is_configured:
            try:
                filepath = REPORTS_DIR / documento.filename
                if filepath.is_file():
                    with open(filepath, "rb") as f:
                        file_bytes = f.read()

                    content_types = {
                        "pdf": "application/pdf",
                        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    }
                    c_type = content_types.get(fmt, "application/octet-stream")

                    reclamo_id = (params or {}).get("numero_reclamo") or (params or {}).get("reclamo_id")
                    if reclamo_id:
                        # Reporte asociado a un siniestro/vehículo específico
                        from app.controls.crashnet_vision_control import crashnet_vision_control
                        poliza_id = (params or {}).get("numero_poliza") or (params or {}).get("poliza_id")
                        cli_doc, veh_placa = crashnet_vision_control.resolver_jerarquia_cliente_vehiculo(poliza_id, reclamo_id)
                        s3_key = s3_storage_service.construir_s3_key_incidente(
                            cliente_id=cli_doc,
                            vehiculo_id=veh_placa,
                            reclamo_id=str(reclamo_id),
                            categoria="reportes",
                            nombre_archivo=documento.filename
                        )
                    else:
                        # Reporte gerencial global (Solvencia, Ventas, Fraude SIU)
                        s3_key = s3_storage_service.construir_s3_key_global(
                            categoria="reportes-globales",
                            nombre_archivo=documento.filename
                        )

                    s3_url = s3_storage_service.subir_bytes(
                        datos_bytes=file_bytes,
                        s3_key=s3_key,
                        content_type=c_type,
                        metadata={"titulo": titulo[:80]}
                    )

                    if s3_url:
                        presigned = s3_storage_service.generar_presigned_download_url(s3_key, expiracion_segundos=900)
                        documento.download_url = presigned or s3_url
                        documento.s3_bucket = s3_storage_service.bucket
                        documento.s3_key = s3_key
                        documento.s3_storage_enabled = True
            except Exception as e_s3:
                print(f"[VoiceMcpControl] Advertencia al subir reporte dual a S3: {e_s3}")

        return documento

    def procesarComandoVozCompleto(
        self,
        audio_bytes: Optional[bytes] = None,
        texto_dictado: Optional[str] = None,
        formato_preferido: Optional[str] = None,
        herramienta_sugerida: Optional[str] = None,
        parametros_manuales: Optional[Dict[str, Any]] = None
    ) -> VoiceMcpExecutionResponse:
        """
        Pipeline principal orquestado:
        1. Transcribe audio vía Whisper STT (Modo A)
        2. Aplica filtro de seguridad estricto OWASP Anti-SQLi
        3. Si es ataque: Aborta inmediatamente con código de amenaza
        4. Si es seguro: Ejecuta Tool MCP con consultas parametrizadas
        5. Compila el reporte físico en Excel, PDF o Word
        """
        # Paso 1: Transcripción Whisper STT
        texto, herramienta_detectada, formato_detectado, params = self.transcribirAudioWhisper(
            audio_bytes=audio_bytes,
            texto_dictado=texto_dictado,
            formato=formato_preferido or "auto"
        )

        # Inferencia Autónoma por Intención / NLP:
        # La intención detectada desde el texto o la voz SIEMPRE prevalece sobre sugerencias estáticas
        if herramienta_detectada and herramienta_detectada != "tool_reporte_siniestralidad":
            herramienta = herramienta_detectada
        elif herramienta_sugerida:
            herramienta = herramienta_sugerida
        else:
            herramienta = herramienta_detectada or "tool_reporte_siniestralidad"

        # Resolución con Prioridad Absoluta al Usuario (Sin restricciones del Auto-IA):
        # 1. Prioridad: Si el usuario seleccionó un formato manual explícito en el UI
        pref_limpio = (formato_preferido or "").lower().strip()
        if pref_limpio in ["pantalla", "xlsx", "pdf", "docx"]:
            formato_final = pref_limpio
        # 2. Prioridad: Si el usuario dictó explícitamente el formato en lenguaje natural
        elif formato_detectado and formato_detectado in ["pantalla", "xlsx", "pdf", "docx"]:
            formato_final = formato_detectado
        # 3. Fallback: Inferencia Autónoma por Dominio (Auto-IA)
        else:
            if herramienta in ["tool_reporte_ventas_primas", "tool_solvencia_reservas"]:
                formato_final = "xlsx"
            elif herramienta == "tool_reporte_auditoria_fraude_siu":
                formato_final = "docx"
            else:
                formato_final = "pdf"

        if parametros_manuales:
            params.update(parametros_manuales)
        params["formato"] = formato_final

        # Paso 2: Blindaje de Ciberseguridad OWASP Anti-SQLi
        auditoria = self.auditarSeguridadAntiSQLi(texto)

        # Paso 3: Neutralización inmediata de amenazas
        if auditoria.es_amenaza:
            traza_bloqueada = McpToolInvocationTraceDTO(
                tool_name=herramienta,
                arguments=params,
                execution_time_ms=0.0,
                records_processed=0,
                status="BLOCKED",
                fuente_datos="Ninguna (Ejecución abortada por política OWASP)"
            )
            return VoiceMcpExecutionResponse(
                transcripcion=texto,
                intencion_detectada="ATAQUE_SQLI_BLOQUEADO",
                formato_solicitado=formato_final,
                auditoria_seguridad=auditoria,
                traza_mcp=traza_bloqueada,
                kpis_resumen={"estado_seguridad": "ALERTA_CRITICA", "amenaza_neutralizada": True},
                documento=None,
                mensaje=f"🚨 Alerta de Seguridad OWASP: Intento de Inyección SQL neutralizado [{auditoria.rule_triggered}]. Consulta bloqueada."
            )

        # Archivo pericial de audio en Amazon S3 (para trazabilidad y auditoría legal)
        if audio_bytes and s3_storage_service.is_configured:
            try:
                rec_id = params.get("numero_reclamo") or params.get("reclamo_id")
                if rec_id:
                    from app.controls.crashnet_vision_control import crashnet_vision_control
                    pol_id = params.get("numero_poliza") or params.get("poliza_id")
                    cli_doc, veh_placa = crashnet_vision_control.resolver_jerarquia_cliente_vehiculo(pol_id, str(rec_id))
                    audio_key = s3_storage_service.construir_s3_key_incidente(
                        cliente_id=cli_doc,
                        vehiculo_id=veh_placa,
                        reclamo_id=str(rec_id),
                        categoria="audios",
                        nombre_archivo=f"audio_declaracion_{int(time.time())}.wav"
                    )
                else:
                    audio_key = s3_storage_service.construir_s3_key_global(
                        categoria="audios-voz",
                        nombre_archivo=f"audio_declaracion_{int(time.time())}.wav"
                    )

                s3_storage_service.subir_bytes(
                    datos_bytes=audio_bytes,
                    s3_key=audio_key,
                    content_type="audio/wav",
                    metadata={"threat_score": str(auditoria.threat_score)}
                )
            except Exception as e_audio:
                print(f"[VoiceMcpControl] Advertencia al subir audio a S3: {e_audio}")
                print(f"[VoiceMcpControl] Advertencia al archivar audio en S3: {e_audio}")

        # Paso 4: Ejecución segura de herramienta MCP
        titulo, kpis, cols, filas, traza = self.ejecutarHerramientaMCP(herramienta, params)

        # Paso 5: Generación física del documento (.xlsx, .pdf, .docx) o entrega en pantalla
        if formato_final == "pantalla":
            documento = None
            mensaje = f"✅ Consulta procesada con éxito. Visualizando {len(filas)} registros en pantalla sin restricciones."
        else:
            documento = self.exportarReporteDocumento(
                titulo=titulo,
                kpis=kpis,
                columnas=cols,
                filas=filas,
                formato=formato_final,
                nombre_base=herramienta.replace("tool_", "reporte_"),
                params=params
            )
            mensaje = f"✅ Comando de voz procesado con éxito. Reporte '{documento.filename}' compilado en formato {formato_final.upper()} listo para descarga."

        return VoiceMcpExecutionResponse(
            transcripcion=texto,
            intencion_detectada=herramienta,
            formato_solicitado=formato_final,
            auditoria_seguridad=auditoria,
            traza_mcp=traza,
            kpis_resumen=kpis,
            columnas=cols,
            filas=filas[:50],
            documento=documento,
            mensaje=mensaje
        )

    def exportarDocumentoEnCaliente(
        self,
        titulo: str,
        kpis: Dict[str, Any],
        columnas: List[str],
        filas: List[Dict[str, Any]],
        formato: str = "pdf",
        nombre_base: str = "reporte_generativo",
        params: Optional[Dict[str, Any]] = None
    ) -> GeneratedDocumentDTO:
        """
        Operación UML 2.5+: exportarDocumentoEnCaliente()
        Permite compilar instantáneamente (< 200 ms) un reporte a partir de datos ya presentes
        en pantalla hacia Excel, PDF o Word, sin reejecutar consultas a la base de datos.
        """
        return self.exportarReporteDocumento(
            titulo=titulo,
            kpis=kpis,
            columnas=columnas,
            filas=filas,
            formato=formato,
            nombre_base=nombre_base,
            params=params
        )

    def obtenerCatalogoTools(self) -> List[McpToolDefinitionDTO]:
        """Retorna el catálogo de herramientas disponibles en el servidor MCP."""
        return self.mcp_server.list_tools()
