"""
=============================================================================
 AegisCore AI - MS4: [ENTITY] DTOs y Esquemas para CU11
 Deep Learning TensorFlow / Keras CNN CrashNet
 Visión Artificial para Peritaje de Daños en Fotos y Videos
 Metodología ICONIX - Capa de Entidad / Contratos de Datos
=============================================================================
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BoundingBoxDTO(BaseModel):
    """Coordenadas relativas y polígono SVG para el visor interactivo de daños."""
    ymin: float = Field(..., description="Coordenada Y mínima normalizada (0.0 a 1.0)")
    xmin: float = Field(..., description="Coordenada X mínima normalizada (0.0 a 1.0)")
    ymax: float = Field(..., description="Coordenada Y máxima normalizada (0.0 a 1.0)")
    xmax: float = Field(..., description="Coordenada X máxima normalizada (0.0 a 1.0)")
    polygon_points: Optional[str] = Field(None, description="Puntos SVG para renderizar el polígono deformado")


class DetectedPartDTO(BaseModel):
    """Representa una pieza automotriz identificada con su porcentaje de daño y costo OEM."""
    parte_id: str = Field(..., description="Identificador único de la zona (ej: bumper, headlamp, hood, fender, door)")
    nombre_pieza: str = Field(..., description="Nombre comercial/técnico de la pieza averiada")
    confianza_deteccion: float = Field(..., description="Probabilidad de inferencia de la red convolucional (0.0 a 1.0)")
    porcentaje_severidad: float = Field(..., description="Grado de deformación física (0% a 100%)")
    accion_recomendada: str = Field(..., description="REEMPLAZO o REPARACION")
    codigo_oem: str = Field(..., description="Número de parte oficial del fabricante (ej: OEM #1493720-00-A)")
    costo_pieza_usd: float = Field(..., description="Precio del repuesto original en USD")
    costo_mano_obra_usd: float = Field(..., description="Costo de hojalatería y pintura o montaje")
    costo_total_usd: float = Field(..., description="Costo total de arreglo para la pieza en USD")
    tiempo_estimado_despacho: str = Field(default="ETA: 24h (In Stock)", description="Disponibilidad en centro logístico")
    bounding_box: Optional[BoundingBoxDTO] = Field(None, description="Bounding Box o polígono de visualización")
    descripcion_dano: str = Field(..., description="Descripción técnica del daño estructural observado")


class KeyframeDTO(BaseModel):
    """Representa un fotograma clave extraído de un video de colisión vehicular."""
    keyframe_id: str = Field(..., description="Identificador único del keyframe (ej: frame_01)")
    timestamp_segundos: float = Field(..., description="Segundo exacto en la línea de tiempo del video")
    label: str = Field(..., description="Etiqueta descriptiva (ej: Frame 02: Pico de Deformación)")
    imagen_url: str = Field(..., description="Imagen del cuadro para renderizar en el canvas")
    severidad_frame: float = Field(..., description="Severidad estructural computada para este cuadro (0.0 a 1.0)")
    piezas_averiadas: List[DetectedPartDTO] = Field(default_factory=list, description="Piezas detectadas en este cuadro")


class DamageAnalysisInputDTO(BaseModel):
    """Payload de entrada para auditar una imagen o video con la red convolucional CrashNet."""
    numero_reclamo: str = Field(default="REC-2026-00492", description="Identificador único del expediente de siniestro")
    reclamo_id: Optional[str] = Field(None, description="Alias para numero_reclamo")
    numero_poliza: Optional[str] = Field("POL-2026-AUT-00892", description="Código de la póliza de seguros")
    poliza_id: Optional[str] = Field(None, description="Alias para numero_poliza")
    imagen_url: Optional[str] = Field(None, description="URL pública o interna de la fotografía de colisión")
    imagen_base64: Optional[str] = Field(None, description="Contenido de la imagen codificado en Base64")
    video_base64: Optional[str] = Field(None, description="Contenido del video codificado en Base64")
    es_video: bool = Field(default=False, description="True si la evidencia corresponde a un video .mp4")
    angulo_toma: Optional[str] = Field("AUTO", description="Perspectiva de la captura: AUTO (inferida por IA), FRONTAL, TRES_CUARTOS_DERECHO, LATERAL, etc.")
    modelo_vehiculo: Optional[str] = Field("Tesla Model Y / SUV", description="Marca y modelo del vehículo asegurado")
    valor_comercial_usd: Optional[float] = Field(None, description="Valor comercial declarado del vehículo si se ingresa manualmente")
    evidencias_galeria: Optional[List[str]] = Field(default=None, description="Lista opcional de imágenes Base64/URLs multi-ángulo")

    def get_numero_reclamo(self) -> str:
        return self.reclamo_id or self.numero_reclamo

    def get_numero_poliza(self) -> str:
        return self.poliza_id or self.numero_poliza or "POL-2026-AUT-00892"

    model_config = {
        "json_schema_extra": {
            "example": {
                "numero_reclamo": "REC-2026-00492",
                "numero_poliza": "POL-2026-AUT-00892",
                "imagen_url": "https://storage.aegiscore.com/evidencias/rec-00492-frontal.jpg",
                "angulo_toma": "FRONTAL_CUARTO_DERECHO",
                "modelo_vehiculo": "Tesla Model Y Long Range 2024"
            }
        }
    }


class FinancialSettlementDTO(BaseModel):
    """Desglose financiero preliminar derivado del peritaje técnico."""
    costo_repuestos_usd: float = Field(..., description="Suma total de piezas a reemplazar")
    costo_mano_obra_usd: float = Field(..., description="Suma total de mano de obra y enderezado")
    costo_total_reparacion_usd: float = Field(..., description="Costo total bruto de reparación")
    deducible_calculado_usd: float = Field(..., description="Deducible a cargo del asegurado según contrato")
    monto_indemnizable_neto_usd: float = Field(..., description="Monto neto a liquidar por la aseguradora")


class DamageAssessmentOutputDTO(BaseModel):
    """Diagnóstico consolidado de visión artificial y peritaje automatizado."""
    numero_reclamo: str
    numero_poliza: Optional[str] = None
    imagen_analizada: str
    modelo_deep_learning: str = Field(default="TensorFlow-CrashNet-CNN-v2.1")
    gravedad_global: str = Field(..., description="LEVE, MEDIA, GRAVE o PÉRDIDA_TOTAL")
    score_danos_global: float = Field(..., description="Índice continuo de severidad (0.0 a 1.0)")
    piezas_averiadas: List[DetectedPartDTO] = Field(default_factory=list)
    liquidacion_financiera: FinancialSettlementDTO
    lidar_telemetria: Dict[str, Any] = Field(default_factory=dict)
    estres_termico: Dict[str, Any] = Field(default_factory=dict)
    keyframes: Optional[List[KeyframeDTO]] = Field(default=None, description="Fotogramas clave extraídos si la evidencia es un video")
    es_video: bool = Field(default=False, description="True si la inspección proviene de un video")
    vehiculo_intacto: bool = Field(default=False, description="True si el peritaje no detectó colisión ni daños")
    orientacion_detectada: str = Field(default="FRONTAL", description="Orientación inferida por IA: FRONTAL, TRES_CUARTOS_DERECHO, TRES_CUARTOS_IZQUIERDO, LATERAL, POSTERIOR")
    valor_comercial_vehiculo_usd: float = Field(default=28000.0, description="Valor comercial obtenido de la póliza PostgreSQL")
    ratio_dano_valor_comercial_pct: float = Field(default=0.0, description="Porcentaje del costo de reparación frente al valor comercial")
    es_perdida_total_50: bool = Field(default=False, description="True si el daño excede el 50% del valor comercial")
    mensaje_dictamen_actuarial: Optional[str] = Field(default=None, description="Dictamen técnico sobre reparabilidad vs pérdida total")
    evidencias_galeria: Optional[List[Dict[str, Any]]] = Field(default=None, description="Galería de tomas in-situ analizadas")
    estado_peritaje: str = Field(default="PERITAJE_COMPLETADO")
    s3_evidencia_url: Optional[str] = Field(default=None, description="URL en S3 de la foto original")
    s3_foto_anotada_url: Optional[str] = Field(default=None, description="URL en S3 de la foto con deteccion IA")
    s3_telemetria_lidar_url: Optional[str] = Field(default=None, description="URL en S3 de la telemetria LiDAR")
    s3_dictamen_pdf_url: Optional[str] = Field(default=None, description="URL en S3 del dictamen pericial en PDF")
    s3_bucket: Optional[str] = Field(default=None, description="Bucket de almacenamiento")
    s3_key_evidencia: Optional[str] = Field(default=None, description="Key S3 de la evidencia")
    s3_key_dictamen: Optional[str] = Field(default=None, description="Key S3 del PDF del dictamen")
    local_dictamen_pdf_url: Optional[str] = Field(default=None, description="URL de respaldo local del dictamen")
    timestamp: str


class ConfirmAssessmentResponseDTO(BaseModel):
    """Confirmación tras asentar el peritaje en MongoDB Atlas e iniciar la liquidación."""
    numero_reclamo: str
    nuevo_estado: str = Field(default="PERITAJE_COMPLETADO")
    monto_aprobado_usd: float
    mensaje: str
    persistencia_mongo_id: Optional[str] = None
    timestamp: str
