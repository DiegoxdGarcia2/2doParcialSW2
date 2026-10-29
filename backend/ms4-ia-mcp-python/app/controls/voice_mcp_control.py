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
from typing import Optional, Dict, Any, List, Tuple

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
        nombre_base: str = "reporte_mcp"
    ) -> GeneratedDocumentDTO:
        """
        Operación UML 2.5+: exportarReporteDocumento()
        Compila el archivo descargable según el formato solicitado (.xlsx, .pdf o .docx).
        """
        fmt = formato.lower().strip()
        if fmt == "xlsx":
            return ExcelDocumentExporter.generar_reporte(titulo, kpis, columnas, filas, nombre_base)
        elif fmt == "docx":
            return WordDocumentExporter.generar_reporte(titulo, kpis, columnas, filas, nombre_base)
        else:
            return PdfDocumentExporter.generar_reporte(titulo, kpis, columnas, filas, nombre_base)

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

        # Resolución Dinámica Autónoma del Formato:
        if formato_detectado and formato_detectado in ["xlsx", "pdf", "docx"]:
            formato_final = formato_detectado
        elif formato_preferido and formato_preferido.lower() in ["xlsx", "pdf", "docx"]:
            formato_final = formato_preferido.lower()
        else:
            # Inferencia según naturaleza de los datos del dominio asegurador:
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

        # Paso 4: Ejecución segura de herramienta MCP
        titulo, kpis, cols, filas, traza = self.ejecutarHerramientaMCP(herramienta, params)

        # Paso 5: Generación física del documento (.xlsx, .pdf, .docx)
        documento = self.exportarReporteDocumento(
            titulo=titulo,
            kpis=kpis,
            columnas=cols,
            filas=filas,
            formato=formato_final,
            nombre_base=herramienta.replace("tool_", "reporte_")
        )

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
            mensaje=f"✅ Comando de voz procesado con éxito. Reporte '{documento.filename}' generado y listo para descarga."
        )

    def obtenerCatalogoTools(self) -> List[McpToolDefinitionDTO]:
        """Retorna el catálogo de herramientas disponibles en el servidor MCP."""
        return self.mcp_server.list_tools()
