"""
=============================================================================
 AegisCore AI - MS4: Entidades y DTOs para el Servidor MCP de Reportes por Voz
 Caso de Uso 15 (CU15) — ICONIX: Estereotipo Entity
 Define modelos Pydantic v2 para:
   - Entrada de comando de voz o texto dictado
   - Auditoría de seguridad OWASP Anti-SQLi
   - Trazas de ejecución del protocolo MCP (Model Context Protocol)
   - Metadatos de documentos generados (Excel, PDF, Word)
=============================================================================
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class VoiceCommandRequest(BaseModel):
    """Solicitud de comando de voz o texto dictado hacia el servidor MCP."""
    prompt_dictado: Optional[str] = Field(
        default=None,
        description="Texto dictado por el usuario o transcrito por el micrófono",
        examples=["Generar reporte de siniestros de alta severidad en formato PDF"]
    )
    formato_preferido: Optional[str] = Field(
        default=None,
        description="Formato de salida deseado: xlsx, pdf o docx (None para resolución autónoma)",
        examples=["xlsx", "pdf", "docx"]
    )
    herramienta_sugerida: Optional[str] = Field(
        default=None,
        description="Nombre explícito de herramienta MCP a invocar (opcional)"
    )
    parametros_manuales: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Parámetros manuales adicionales para sobreescribir la inferencia fonética"
    )


class OwaspSecurityAuditDTO(BaseModel):
    """Resultado del análisis léxico y de AST para neutralizar inyecciones SQL."""
    es_amenaza: bool = Field(description="True si se detectó un vector de inyección SQL o payload malicioso")
    threat_score: float = Field(ge=0.0, le=1.0, description="Puntuación de riesgo de 0.0 (seguro) a 1.0 (crítico)")
    rule_triggered: Optional[str] = Field(default=None, description="Regla OWASP infringida")
    payload_original: str = Field(description="Payload original analizado")
    payload_sanitizado: str = Field(description="Texto sanitizado y libre de caracteres de escape")
    detalles_inspeccion: List[str] = Field(default_factory=list, description="Hallazgos del analizador léxico")
    estado: str = Field(default="SAFE", description="SAFE o BLOCKED")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class McpToolDefinitionDTO(BaseModel):
    """Definición formal de herramienta bajo el estándar Model Context Protocol (Anthropic/Linux Foundation)."""
    name: str = Field(description="Identificador único de la herramienta MCP")
    description: str = Field(description="Descripción funcional para el modelo / orquestador")
    inputSchema: Dict[str, Any] = Field(description="Esquema JSON Schema de los argumentos aceptados")


class McpToolInvocationTraceDTO(BaseModel):
    """Traza de invocación y telemetría de la herramienta MCP."""
    tool_name: str = Field(description="Herramienta MCP ejecutada")
    arguments: Dict[str, Any] = Field(description="Argumentos validados y tipados")
    execution_time_ms: float = Field(description="Latencia de ejecución en milisegundos")
    records_processed: int = Field(description="Cantidad de registros procesados desde BD")
    status: str = Field(default="SUCCESS", description="SUCCESS, ERROR o BLOCKED")
    fuente_datos: str = Field(description="Origen de persistencia: Neon PostgreSQL o MongoDB Atlas")


class GeneratedDocumentDTO(BaseModel):
    """Metadatos del archivo físico compilado listo para descarga por HTTP streaming."""
    filename: str = Field(description="Nombre físico del archivo en el servidor")
    format: str = Field(description="xlsx, pdf o docx")
    file_size_bytes: int = Field(description="Tamaño en bytes")
    file_size_kb: float = Field(description="Tamaño en kilobytes")
    sha256_hash: str = Field(description="Firma criptográfica SHA-256 para validación de integridad")
    download_url: str = Field(description="URL directa para descarga por HTTP streaming")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class VoiceMcpExecutionResponse(BaseModel):
    """Respuesta unificada de procesamiento de comando de voz con MCP y OWASP."""
    transcripcion: str = Field(description="Texto transcrito por Whisper STT o texto dictado")
    intencion_detectada: str = Field(description="Intención de negocio clasificada")
    formato_solicitado: str = Field(description="Formato del reporte generado")
    auditoria_seguridad: OwaspSecurityAuditDTO = Field(description="Inspección de seguridad OWASP Anti-SQLi")
    traza_mcp: Optional[McpToolInvocationTraceDTO] = Field(default=None, description="Telemetría de la herramienta MCP")
    kpis_resumen: Dict[str, Any] = Field(default_factory=dict, description="Métricas ejecutivas clave extraídas")
    columnas: List[str] = Field(default_factory=list, description="Nombres de columnas de la tabla generada")
    filas: List[Dict[str, Any]] = Field(default_factory=list, description="Filas tabulares procesadas para previsualización inmediata en navegador")
    documento: Optional[GeneratedDocumentDTO] = Field(default=None, description="Metadatos del archivo descargable")
    mensaje: str = Field(description="Mensaje legible para el usuario o perito")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
