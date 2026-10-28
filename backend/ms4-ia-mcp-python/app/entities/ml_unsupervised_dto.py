"""
=============================================================================
 AegisCore AI - MS4: [ENTITY] DTOs y Esquemas para CU13
 Machine Learning No Supervisado (K-Means Clustering + Isolation Forest)
 Metodología ICONIX - Capa de Entidad / Contratos de Datos
=============================================================================
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ClusterProfileDTO(BaseModel):
    """
    Perfil consolidado de un cluster de asegurados descubierto por K-Means.
    """
    cluster_id: int = Field(..., description="Identificador numérico del cluster (0, 1, 2...)")
    nombre: str = Field(..., description="Etiqueta semántica de negocio para el cluster")
    total_asegurados: int = Field(..., description="Cantidad de pólizas asignadas a este segmento")
    porcentaje_flota: float = Field(..., description="Porcentaje relativo sobre el total de la cartera (%)")
    edad_media: float = Field(..., description="Edad promedio de los conductores en el cluster")
    valor_vehiculo_medio_usd: float = Field(..., description="Valor comercial promedio de los vehículos (USD)")
    frecuencia_siniestros_anual: float = Field(..., description="Tasa media de siniestros anuales por conductor")
    score_riesgo_medio: float = Field(..., description="Puntuación actuarial media de riesgo (0-100)")
    prima_recomendada_descuento: str = Field(..., description="Estrategia actuarial de ajuste tarifario sugerida")


class FraudAlertDTO(BaseModel):
    """
    Representa una alerta de anomalía o sospecha de fraude detectada por Isolation Forest
    y persistida en MongoDB Atlas (colección alertas_fraude_anomalias).
    """
    reclamo_id: str = Field(..., description="Código de reclamo vial o médico (ej. REC-2026-00492)")
    poliza_id: Optional[str] = Field(None, description="UUID o código de la póliza asegurada")
    monto_solicitado_usd: float = Field(..., description="Monto en USD reclamado por el taller o asegurado")
    monto_promedio_mercado_usd: float = Field(..., description="Costo medio de mercado para el tipo de daño y vehículo")
    divergencia_porcentaje: float = Field(..., description="Porcentaje de sobreprecio o desvío respecto a la norma")
    score_anomalia: float = Field(..., description="Puntuación continua de Isolation Forest (menor a 0 = anómalo)")
    es_anomalo: bool = Field(..., description="Flag booleano que determina si supera el umbral de aislamiento")
    nivel_criticidad: str = Field(..., description="CRÍTICO, ALTO, MEDIO o NORMAL")
    taller_mecanico: Optional[str] = Field("Taller Autorizado Regional", description="Nombre del taller emisor")
    motivo_sospecha: str = Field(..., description="Explicación matemática y actuarial de la anomalía detectada")
    estado_pago: str = Field(default="PENDIENTE_REVISION", description="PENDIENTE_REVISION, CONGELADO_PREVENTIVO_SAGA, AUDITADO, APROBADO")
    fecha_alerta: str = Field(..., description="Marca de tiempo ISO del registro de la anomalía")


class EvaluateClaimInputDTO(BaseModel):
    """
    Parámetros de entrada para auditar un nuevo siniestro en tiempo real con Isolation Forest.
    """
    reclamo_id: str = Field(default="REC-2026-00501", description="Identificador único del siniestro")
    poliza_id: Optional[str] = Field("POL-2026-AUT-00100", description="Código de póliza vinculada")
    edad_conductor: int = Field(default=32, ge=18, le=90, description="Edad del conductor al momento del choque")
    tipo_vehiculo: str = Field(default="SUV", description="SUV, CAMIONETA, HATCHBACK, SEDAN, MOTOCICLETA")
    valor_comercial_usd: float = Field(default=25000.0, ge=1000.0, description="Valor comercial del vehículo")
    monto_solicitado_usd: float = Field(default=6800.0, ge=50.0, description="Monto de presupuesto o indemnización solicitado")
    dias_desde_emision: int = Field(default=18, ge=0, description="Días transcurridos entre la emisión de póliza y el choque")
    historial_siniestros: int = Field(default=2, ge=0, description="Siniestros reportados previamente")
    taller_mecanico: Optional[str] = Field("Taller Mecánico El Progreso", description="Nombre del taller que cotiza el arreglo")

    model_config = {
        "json_schema_extra": {
            "example": {
                "reclamo_id": "REC-2026-00402",
                "poliza_id": "POL-2026-AUT-99120",
                "edad_conductor": 22,
                "tipo_vehiculo": "SEDAN",
                "valor_comercial_usd": 14000.0,
                "monto_solicitado_usd": 9200.0,
                "dias_desde_emision": 5,
                "historial_siniestros": 3,
                "taller_mecanico": "Taller Multimarca San Cristóbal"
            }
        }
    }


class FraudDashboardSummaryDTO(BaseModel):
    """
    Resumen consolidado para la vista "Risk & Fraud Sentinel" en Angular.
    """
    threat_index_percentage: float = Field(..., description="Índice de amenaza global de la flota (Threat Gauge SVG)")
    threat_level_label: str = Field(..., description="LOW, LOW-MODERATE, MODERATE, HIGH, CRITICAL")
    perdidas_prevenidas_usd: float = Field(..., description="Monto total en USD retenido por detección temprana de fraude")
    total_siniestros_auditados: int = Field(..., description="Total de reclamos analizados por Isolation Forest")
    total_alertas_activas: int = Field(..., description="Cantidad de reclamos bajo sospecha activa de fraude")
    silhouette_score_kmeans: float = Field(..., description="Coeficiente de silueta que valida la separación de clusters")
    clusters_kmeans: List[ClusterProfileDTO] = Field(default_factory=list)
    alertas_recientes: List[FraudAlertDTO] = Field(default_factory=list)
    timestamp: str = Field(..., description="Fecha y hora ISO del reporte analítico")


class FreezeClaimResponseDTO(BaseModel):
    """
    Respuesta tras congelar preventivamente el pago en MongoDB Atlas.
    """
    reclamo_id: str
    estado_anterior: str
    nuevo_estado: str
    score_anomalia: float
    mensaje: str
    persistencia_mongo_id: Optional[str] = None
    timestamp: str
