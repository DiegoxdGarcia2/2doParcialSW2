"""
=============================================================================
 AegisCore AI - MS4: Suite de Pruebas Unitarias para Caso de Uso 15 (CU15)
 Servidor MCP, Whisper STT, Blindaje OWASP Anti-SQLi y Exportadores Documentales
=============================================================================
"""

import os
from pathlib import Path
import pytest
from app.entities.voice_mcp_dto import VoiceCommandRequest
from app.mcp_voice_reports.security.owasp_antisqli_guard import OwaspAntiSqliGuard
from app.mcp_voice_reports.stt.whisper_engine import WhisperSTTEngine
from app.mcp_voice_reports.server.mcp_protocol_server import McpProtocolServer
from app.mcp_voice_reports.exporters.excel_exporter import ExcelDocumentExporter
from app.mcp_voice_reports.exporters.pdf_exporter import PdfDocumentExporter
from app.mcp_voice_reports.exporters.word_exporter import WordDocumentExporter
from app.controls.voice_mcp_control import VoiceMcpControl


class TestCU15VoiceMcpReports:

    def setup_method(self):
        self.control = VoiceMcpControl()

    # -------------------------------------------------------------------------
    # 1. Pruebas de Blindaje de Ciberseguridad OWASP Anti-SQLi
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize("payload,regla_esperada", [
        ("reporte de siniestros ' OR '1'='1", "OWASP-A03:SQLi-Tautology"),
        ("mostrar polizas' OR 1=1 --", "OWASP-A03:SQLi-Tautology"),
        ("siniestros UNION SELECT username, password FROM usuarios", "OWASP-A03:SQLi-UnionBased"),
        ("reporte anual ; DROP TABLE poliza; --", "OWASP-A03:SQLi-StackedQueries"),
        ("consultar reserva ; EXEC xp_cmdshell('dir')", "OWASP-A03:SQLi-SystemExecution"),
        ("ver facturas WHERE id = 1 AND benchmark(10000000, MD5(1))", "OWASP-A03:SQLi-TimeBlind"),
        ("obtener datos de information_schema.tables", "OWASP-A03:SQLi-InformationSchema"),
    ])
    def test_owasp_anti_sqli_blocks_malicious_payloads(self, payload, regla_esperada):
        """Valida que todos los vectores de inyección SQL sean bloqueados con amenaza detectada."""
        auditoria = OwaspAntiSqliGuard.auditar_texto(payload)
        assert auditoria.es_amenaza is True
        assert auditoria.estado == "BLOCKED"
        assert auditoria.threat_score >= 0.70
        assert auditoria.rule_triggered is not None

    def test_owasp_anti_sqli_allows_legitimate_prompts(self):
        """Valida que consultas legítimas en lenguaje natural sean aprobadas con SAFE."""
        prompts_validos = [
            "Generar reporte de siniestralidad de vehículos SUV en formato PDF",
            "Auditoría de fraudes con severidad alta en Excel",
            "Reporte actuarial de primas proyectadas para camionetas en Word",
            "Solvencia técnica y reservas de fin de año en formato PDF"
        ]
        for prompt in prompts_validos:
            auditoria = OwaspAntiSqliGuard.auditar_texto(prompt)
            assert auditoria.es_amenaza is False
            assert auditoria.estado == "SAFE"
            assert auditoria.threat_score == 0.0

    # -------------------------------------------------------------------------
    # 2. Pruebas de Transcripción e Intención Whisper STT (Modo A)
    # -------------------------------------------------------------------------
    def test_whisper_stt_intent_and_format_extraction(self):
        """Valida extracción de herramienta, formato y parámetros desde lenguaje natural."""
        texto = "Generar reporte de siniestros de alta severidad en formato Excel"
        t_out, tool, fmt, params = WhisperSTTEngine.transcribir_audio(texto_fallback=texto)

        assert t_out == texto
        assert tool == "tool_reporte_siniestralidad"
        assert fmt == "xlsx"
        assert params.get("severidad") == "ALTA"

    def test_whisper_stt_audio_bytes_decoding(self):
        """Valida decodificación de tramas de audio binarias sintéticas."""
        dummy_wav = b"RIFF" + b"\x00" * 40 + b"prompt_dictado: Auditoria de fraudes SIU en Word"
        t_out, tool, fmt, params = WhisperSTTEngine.transcribir_audio(audio_bytes=dummy_wav)

        assert "Auditoria de fraudes" in t_out
        assert tool == "tool_reporte_auditoria_fraude_siu"
        assert fmt == "docx"

    # -------------------------------------------------------------------------
    # 3. Pruebas del Catálogo de Herramientas MCP
    # -------------------------------------------------------------------------
    def test_mcp_tools_catalog_specification(self):
        """Valida que el catálogo exponga las 4 herramientas con JSON Schema estricto."""
        tools = McpProtocolServer.list_tools()
        assert len(tools) == 4
        tool_names = [t.name for t in tools]
        assert "tool_reporte_siniestralidad" in tool_names
        assert "tool_reporte_ventas_primas" in tool_names
        assert "tool_reporte_auditoria_fraude_siu" in tool_names
        assert "tool_solvencia_reservas" in tool_names

        for t in tools:
            assert "type" in t.inputSchema
            assert "properties" in t.inputSchema
            assert "required" in t.inputSchema

    # -------------------------------------------------------------------------
    # 4. Pruebas de Generación Documental Física (Excel, PDF, Word)
    # -------------------------------------------------------------------------
    def test_document_generation_excel(self):
        """Valida generación física y firma SHA-256 de planilla Excel (.xlsx)."""
        kpis = {"total_siniestros": 15, "costo_total_usd": "$34,500.00"}
        cols = ["numero_reclamo", "poliza", "severidad", "costo_estimado"]
        filas = [{"numero_reclamo": "REC-001", "poliza": "POL-100", "severidad": "ALTA", "costo_estimado": 2300.0}]

        doc = ExcelDocumentExporter.generar_reporte("Siniestralidad Test", kpis, cols, filas, "test_excel")
        assert doc.format == "xlsx"
        assert doc.file_size_bytes > 0
        assert len(doc.sha256_hash) == 64
        assert os.path.exists(Path(doc.download_url.replace("/api/v1/mcp/download-report/", "artifacts/reports/")))

    def test_document_generation_pdf(self):
        """Valida generación física y firma SHA-256 de informe PDF (.pdf)."""
        kpis = {"total_polizas": 120, "prima_promedio": "$850.00"}
        cols = ["poliza_id", "tipo_vehiculo", "valor_asegurado", "prima_anual_usd"]
        filas = [{"poliza_id": "POL-101", "tipo_vehiculo": "SUV", "valor_asegurado": 28000.0, "prima_anual_usd": 920.0}]

        doc = PdfDocumentExporter.generar_reporte("Primas Test", kpis, cols, filas, "test_pdf")
        assert doc.format == "pdf"
        assert doc.file_size_bytes > 0
        assert len(doc.sha256_hash) == 64

    def test_document_generation_word(self):
        """Valida generación física y firma SHA-256 de minuta Word (.docx)."""
        kpis = {"expedientes_auditados": 8, "divergencia_media": "52.4%"}
        cols = ["reclamo_id", "taller_mecanico", "score_anomalia", "criticidad"]
        filas = [{"reclamo_id": "REC-009", "taller_mecanico": "Taller Sur", "score_anomalia": 0.88, "criticidad": "CRÍTICO"}]

        doc = WordDocumentExporter.generar_reporte("Auditoría SIU Test", kpis, cols, filas, "test_word")
        assert doc.format == "docx"
        assert doc.file_size_bytes > 0
        assert len(doc.sha256_hash) == 64

    # -------------------------------------------------------------------------
    # 5. Pruebas Integradas de la Clase de Control (VoiceMcpControl)
    # -------------------------------------------------------------------------
    def test_control_end_to_end_legitimate_execution(self):
        """Valida flujo integral exitoso con herramienta MCP y archivo descargable."""
        res = self.control.procesarComandoVozCompleto(
            texto_dictado="Generar reporte de siniestralidad de alta severidad en formato PDF",
            formato_preferido="pdf"
        )
        assert res.auditoria_seguridad.es_amenaza is False
        assert res.intencion_detectada == "tool_reporte_siniestralidad"
        assert res.documento is not None
        assert res.documento.format == "pdf"
        assert res.traza_mcp.status == "SUCCESS"

    def test_control_end_to_end_attack_neutralization(self):
        """Valida que un ataque SQLi detenga la ejecución y retorne documento None."""
        res = self.control.procesarComandoVozCompleto(
            texto_dictado="Reporte anual ; DROP TABLE cliente; --",
            formato_preferido="xlsx"
        )
        assert res.auditoria_seguridad.es_amenaza is True
        assert res.intencion_detectada == "ATAQUE_SQLI_BLOQUEADO"
        assert res.documento is None
        assert res.traza_mcp.status == "BLOCKED"
        assert "neutralizado" in res.mensaje.lower()
