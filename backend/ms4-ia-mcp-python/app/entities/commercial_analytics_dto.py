"""
=============================================================================
 AegisCore AI - MS4: [ENTITY] DTOs para Analítica Comercial 360° y Rentabilidad
 Metodología ICONIX - Objeto Entity (Contrato de Datos y Validación Pydantic v2)
 Integración MCP + GraphQL para Análisis Comercial: LTV, CAC, Churn y Conversión
=============================================================================
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


DepartamentoLiteral = Literal["TODOS", "SANTA_CRUZ", "LA_PAZ", "COCHABAMBA", "TARIJA", "CHUQUISACA", "ORURO", "POTOSI", "BENI", "PANDO"]
RamoLiteral = Literal["TODOS", "VEHICULAR", "SALUD", "VIDA", "HOGAR"]
CanalVentaLiteral = Literal["TODOS", "WEB_REACT", "WHATSAPP_N8N", "BROKER", "OFICINA_ANGULAR"]
PeriodoLiteral = Literal["Q1", "Q2", "Q3", "Q4", "YTD", "MENSUAL"]


class CommercialFilterInputDTO(BaseModel):
    """Filtros multidimensionales 360° para segmentación ejecutiva."""
    departamento: DepartamentoLiteral = Field(
        default="TODOS",
        description="Filtro geográfico por departamento o consolidado nacional"
    )
    ramo: RamoLiteral = Field(
        default="TODOS",
        description="Línea de negocio o ramo de seguros (TipoPlan GraphQL)"
    )
    canal: CanalVentaLiteral = Field(
        default="TODOS",
        description="Canal de adquisición y venta de la póliza"
    )
    periodo: PeriodoLiteral = Field(
        default="Q3",
        description="Ventana temporal de análisis (trimestral o acumulada)"
    )


class ChannelEfficiencyDTO(BaseModel):
    """Métricas de eficiencia económica y conversión por canal de distribución."""
    canal: str = Field(..., description="Nombre comercial del canal")
    codigo_canal: str = Field(..., description="Identificador técnico (ej: WEB_REACT)")
    cac_usd: float = Field(..., description="Costo de Adquisición de Clientes en USD")
    conversion_pct: float = Field(..., description="Tasa de conversión de cotización a póliza emitida (%)")
    polizas_vendidas: int = Field(..., description="Volumen total de pólizas captadas")
    ingresos_usd: float = Field(..., description="Primas brutas captadas en USD")
    margen_contribucion_pct: float = Field(..., description="Margen de contribución comercial (%)")


class LtvRetentionTrendDTO(BaseModel):
    """Punto en la serie temporal para la evolución de valor de cliente y retención."""
    mes: str = Field(..., description="Mes calendario (YYYY-MM o etiqueta)")
    ltv_usd: float = Field(..., description="Customer Lifetime Value proyectado en USD")
    retencion_pct: float = Field(..., description="Tasa de retención de cartera activa (%)")
    churn_pct: float = Field(..., description="Tasa de deserción/churn mensual (%)")


class CommercialKpiSummaryDTO(BaseModel):
    """Resumen consolidado para la pestaña de Rentabilidad Comercial y Analítica 360°."""
    prima_media_usd: float = Field(..., description="Prima media emitida en USD")
    cac_promedio_usd: float = Field(..., description="Costo medio ponderado de adquisición en USD")
    ltv_promedio_usd: float = Field(..., description="Customer Lifetime Value promedio en USD")
    ltv_cac_ratio: float = Field(..., description="Ratio de eficiencia comercial (LTV / CAC)")
    churn_anual_pct: float = Field(..., description="Tasa anualizada de deserción de cartera (%)")
    retencion_anual_pct: float = Field(..., description="Tasa anualizada de retención de pólizas (%)")
    tasa_conversion_global_pct: float = Field(..., description="Tasa de conversión promedio de todos los canales (%)")
    polizas_totales: int = Field(..., description="Universo de pólizas consideradas en el corte")
    ingresos_totales_usd: float = Field(..., description="Volumen de primas brutas emitidas (GWP) en USD")
    salud_comercial_label: str = Field(..., description="Evaluación cualitativa (EXCELENTE, OPTIMO, ATENCION)")
    canales_eficiencia: List[ChannelEfficiencyDTO] = Field(..., description="Desglose por canal para gráfico de barras")
    tendencia_mensual: List[LtvRetentionTrendDTO] = Field(..., description="Serie temporal para gráfico de líneas/área")
    filtros_aplicados: CommercialFilterInputDTO = Field(..., description="Filtros utilizados en el cálculo")
    timestamp: str = Field(..., description="Marca de tiempo de generación ISO 8601")


class FilterOptionsDTO(BaseModel):
    """Opciones válidas para poblar los selectores de la Barra de Filtros 360°."""
    departamentos: List[Dict[str, str]]
    ramos: List[Dict[str, str]]
    canales: List[Dict[str, str]]
    periodos: List[Dict[str, str]]

