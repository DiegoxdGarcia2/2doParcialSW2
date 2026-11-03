"""
=============================================================================
 AegisCore AI - MS4: [ENTITY] DTOs para Analítica de Siniestralidad y Riesgo 360°
 Metodología ICONIX - Objeto Entity (Contrato de Datos y Validación Pydantic v2)
 Consultas 100% SQL Puras sobre dataset_historico_ml_polizas en PostgreSQL Neon
=============================================================================
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


TipoVehiculoFilter = Literal["TODOS", "SUV", "CAMIONETA", "HATCHBACK", "MOTOCICLETA", "SEDAN"]
RangoEdadFilter = Literal["TODOS", "18-25", "26-35", "36-50", "51-65", "65+"]
AntiguedadLicenciaFilter = Literal["TODOS", "NOVATO", "INTERMEDIO", "EXPERTO"]
AntiguedadVehiculoFilter = Literal["TODOS", "2020_2023", "2015_2019", "2010_2014"]


class ActuarialLossFilterInputDTO(BaseModel):
    """Filtros multidimensionales 360° aplicados directamente a consultas SQL."""
    tipo_vehiculo: TipoVehiculoFilter = Field(
        default="TODOS",
        description="Filtro por categoría de vehículo (SUV, CAMIONETA, etc.)"
    )
    rango_edad: RangoEdadFilter = Field(
        default="TODOS",
        description="Filtro demográfico por cohorte de edad del conductor asegurado"
    )
    antiguedad_licencia: AntiguedadLicenciaFilter = Field(
        default="TODOS",
        description="Filtro por años de experiencia de conducción (Novato 0-2, Intermedio 3-7, Experto 8+)"
    )
    antiguedad_vehiculo: AntiguedadVehiculoFilter = Field(
        default="TODOS",
        description="Filtro por año de modelo de fabricación del vehículo asegurado"
    )


class VehicleLossMetricDTO(BaseModel):
    """Fila agregada para la Matriz de Riesgo por Tipo de Vehículo."""
    tipo_vehiculo: str = Field(..., description="Categoría de vehículo (ej: CAMIONETA, SUV)")
    total_polizas: int = Field(..., description="Universo de pólizas en la categoría")
    siniestros_count: int = Field(..., description="Total de siniestros ocurridos")
    frecuencia_siniestralidad_pct: float = Field(..., description="Tasa de siniestros (%)")
    costo_medio_usd: float = Field(..., description="Severidad media / Costo promedio de reparación en USD")
    prima_media_usd: float = Field(..., description="Prima media cobrada en USD")
    total_costo_siniestros_usd: float = Field(..., description="Costo total de siniestros pagados en USD")
    total_primas_usd: float = Field(..., description="Volumen total de primas recaudadas en USD")
    loss_ratio_pct: float = Field(..., description="Ratio de siniestralidad técnica: Siniestros / Primas (%)")
    semaforo_tecnico: str = Field(..., description="Evaluación técnica (SUPERÁVIT TÉCNICO, EQUILIBRADO, ALTO RIESGO)")


class AgeCohortMetricDTO(BaseModel):
    """Punto de datos para el Gráfico 1: Siniestralidad y Severidad por Rango de Edad."""
    rango_edad: str = Field(..., description="Etiqueta de la cohorte (ej: 18-25, 26-35)")
    total_conductores: int = Field(..., description="Pólizas emitidas en el rango de edad")
    total_siniestros: int = Field(..., description="Siniestros incurridos en la cohorte")
    frecuencia_pct: float = Field(..., description="Frecuencia de accidentes (%)")
    costo_medio_usd: float = Field(..., description="Severidad promedio del choque en USD")


class MonthlyTrendMetricDTO(BaseModel):
    """Punto en la serie temporal para el Gráfico 2: Evolución Mensual de Incurrencia."""
    mes: str = Field(..., description="Mes calendario (YYYY-MM o etiqueta)")
    polizas_activas: int = Field(..., description="Pólizas activas en el mes")
    siniestros_mes: int = Field(..., description="Accidentes reportados en el mes")
    costo_total_mes_usd: float = Field(..., description="Costo acumulado de reparaciones en USD")
    tasa_incurrencia_pct: float = Field(..., description="Tasa de siniestralidad mensual (%)")


class ActuarialLossSummaryDTO(BaseModel):
    """Resumen consolidado de Siniestralidad y Riesgo Demográfico 360°."""
    # Top 5 Bento KPIs
    frecuencia_siniestralidad_pct: float = Field(..., description="Tasa global de siniestros en la muestra filtrada (%)")
    severidad_media_usd: float = Field(..., description="Costo medio de siniestro cuando ocurre accidente en USD")
    loss_ratio_tecnico_pct: float = Field(..., description="Loss Ratio técnico (Costo Total Siniestros / Total Primas %)")
    prima_media_anual_usd: float = Field(..., description="Prima promedio anual emitida en USD")
    score_medio_riesgo: float = Field(..., description="Score promedio de riesgo actuarial (0 a 100)")
    
    # Metadatos de Universo
    total_polizas: int = Field(..., description="Universo total de pólizas filtradas")
    total_siniestros: int = Field(..., description="Total de accidentes registrados")
    costo_total_siniestros_usd: float = Field(..., description="Monto total liquidado/incurrido en siniestros en USD")
    primas_totales_usd: float = Field(..., description="Monto total de primas recaudadas en USD")
    salud_cartera_label: str = Field(..., description="Etiqueta de solvencia actuarial técnica")
    
    # Datos de Visualizaciones
    desglose_por_vehiculo: List[VehicleLossMetricDTO] = Field(..., description="Datos de la tabla de matriz de vehículos")
    cohortes_edad: List[AgeCohortMetricDTO] = Field(..., description="Datos para Gráfico 1: Barras dobles por edad")
    tendencia_mensual: List[MonthlyTrendMetricDTO] = Field(..., description="Datos para Gráfico 2: Evolución 12 meses cronológicos")
    
    filtros_aplicados: ActuarialLossFilterInputDTO = Field(..., description="Filtros SQL aplicados en la consulta")
    timestamp: str = Field(..., description="Marca de tiempo ISO 8601 de la ejecución")


class ActuarialFilterOptionsDTO(BaseModel):
    """Catálogo de opciones para poblar la barra de filtros en Angular."""
    tipos_vehiculo: List[Dict[str, str]]
    rangos_edad: List[Dict[str, str]]
    antiguedades_licencia: List[Dict[str, str]]
    antiguedades_vehiculo: List[Dict[str, str]]

