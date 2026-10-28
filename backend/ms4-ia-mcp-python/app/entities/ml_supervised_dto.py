"""
=============================================================================
 AegisCore AI - MS4: [ENTITY] DTOs y Esquemas para CU12 (Random Forest)
 Metodología ICONIX - Capa de Entidad / Contratos de Datos
=============================================================================
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class PredictionInputDTO(BaseModel):
    """
    Parámetros de entrada para simulación actuarial y proyección de prima/demanda.
    """
    edad_asegurado: int = Field(default=35, ge=18, le=95, description="Edad del asegurado en años")
    antiguedad_licencia_anios: int = Field(default=10, ge=0, le=75, description="Años de vigencia de licencia de conducir")
    tipo_vehiculo: str = Field(default="SUV", description="Categoría vehicular: SUV, CAMIONETA, HATCHBACK, SEDAN, MOTOCICLETA")
    anio_vehiculo: int = Field(default=2020, ge=1990, le=2027, description="Año de fabricación del vehículo")
    valor_comercial_usd: float = Field(default=25000.0, ge=1000.0, le=250000.0, description="Valor comercial declarado del vehículo")
    historial_siniestros_previos: int = Field(default=0, ge=0, le=10, description="Número de siniestros reportados en los últimos 3 años")
    perfil_riesgo_score: float = Field(default=35.0, ge=0.0, le=100.0, description="Puntuación actuarial previa de riesgo (0-100)")
    meses_a_proyectar: int = Field(default=6, ge=1, le=12, description="Número de meses horizonte para la proyección de ventas")

    model_config = {
        "json_schema_extra": {
            "example": {
                "edad_asegurado": 34,
                "antiguedad_licencia_anios": 12,
                "tipo_vehiculo": "SUV",
                "anio_vehiculo": 2021,
                "valor_comercial_usd": 28000.0,
                "historial_siniestros_previos": 1,
                "perfil_riesgo_score": 45.0,
                "meses_a_proyectar": 6
            }
        }
    }


class MonthlyProjectionDTO(BaseModel):
    """
    Proyección de demanda temporal mes a mes.
    """
    mes: str = Field(..., description="Año y mes proyectado (YYYY-MM)")
    ventas_estimadas_polizas: int = Field(..., description="Cantidad estimada de pólizas a emitir")
    prima_sugerida_usd: float = Field(..., description="Prima media óptima proyectada para el mes")
    intervalo_confianza_min: float = Field(..., description="Cota inferior del 95% de confianza (USD)")
    intervalo_confianza_max: float = Field(..., description="Cota superior del 95% de confianza (USD)")


class FeatureImportanceDTO(BaseModel):
    """
    Ponderación explicable (XAI) de variables en el Random Forest.
    """
    variable: str
    importancia_porcentaje: float


class ModelMetricsDTO(BaseModel):
    """
    Métricas de precisión y calidad del modelo Random Forest.
    """
    r2_score: float = Field(..., description="Coeficiente de determinación R^2 del regresor de primas")
    mae_usd: float = Field(..., description="Error absoluto medio en USD (MAE)")
    rmse_usd: float = Field(..., description="Raíz del error cuadrático medio en USD (RMSE)")
    accuracy_siniestros: float = Field(..., description="Exactitud en la clasificación de probabilidad de siniestro")
    total_registros_entrenamiento: int = Field(default=1200, description="Muestras históricas procesadas")
    n_estimadores: int = Field(default=150, description="Cantidad de árboles en el ensamble")
    feature_importances: List[FeatureImportanceDTO] = Field(default_factory=list)
    fecha_ultimo_entrenamiento: str = Field(..., description="Marca de tiempo ISO del último entrenamiento")


class PredictionOutputDTO(BaseModel):
    """
    Resultado completo de inferencia actuarial y proyecciones.
    """
    prima_anual_optima_usd: float = Field(..., description="Prima técnica sugerida calculada por Random Forest")
    rango_confianza_95: List[float] = Field(..., description="Intervalo [mínimo, máximo] con 95% de certeza")
    desviacion_estandar_usd: float = Field(..., description="Dispersión entre árboles individuales del ensamble")
    probabilidad_siniestro_pct: float = Field(..., description="Probabilidad calculada de sufrir siniestro (0-100%)")
    nivel_riesgo_clasificado: str = Field(..., description="Segmento de riesgo: BAJO, MEDIO, ALTO o CRÍTICO")
    costo_siniestro_estimado_usd: float = Field(..., description="Severidad esperada en caso de evento adverso")
    proyecciones_mensuales: List[MonthlyProjectionDTO] = Field(..., description="Curva temporal de demanda")
    metricas_modelo: ModelMetricsDTO = Field(..., description="Metadatos de precisión del modelo")


class RetrainResponseDTO(BaseModel):
    """
    Respuesta del reentrenamiento del modelo.
    """
    mensaje: str
    registros_cargados: int
    r2_score_nuevo: float
    mae_usd_nuevo: float
    tiempo_ejecucion_segundos: float
    fecha_entrenamiento: str
