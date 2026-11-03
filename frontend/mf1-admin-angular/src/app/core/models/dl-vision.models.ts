/**
 * =============================================================================
 *  AegisCore AI - MF1 Angular: Modelos e Interfaces para CU11
 *  Deep Learning Visión Artificial (TensorFlow CrashNet)
 *  Trazabilidad ICONIX: Capa de Entidad / DTOs
 * =============================================================================
 */

export interface BoundingBox {
  ymin: number;
  xmin: number;
  ymax: number;
  xmax: number;
  polygon_points?: string;
}

export interface DetectedPart {
  parte_id: string;
  nombre_pieza: string;
  confianza_deteccion: number;
  porcentaje_severidad: number;
  accion_recomendada: 'REEMPLAZO' | 'REPARACION';
  codigo_oem: string;
  costo_pieza_usd: number;
  costo_mano_obra_usd: number;
  costo_total_usd: number;
  tiempo_estimado_despacho: string;
  bounding_box?: BoundingBox;
  descripcion_dano: string;
}

export interface Keyframe {
  keyframe_id: string;
  timestamp_segundos: number;
  label: string;
  imagen_url: string;
  severidad_frame: number;
  piezas_averiadas: DetectedPart[];
}

export interface DamageAnalysisInput {
  numero_reclamo: string;
  numero_poliza?: string;
  imagen_url?: string;
  imagen_base64?: string;
  video_base64?: string;
  es_video?: boolean;
  angulo_toma?: string;
  modelo_vehiculo?: string;
  valor_comercial_usd?: number;
  evidencias_galeria?: string[];
}

export interface FinancialSettlement {
  costo_repuestos_usd: number;
  costo_mano_obra_usd: number;
  costo_total_reparacion_usd: number;
  deducible_calculado_usd: number;
  monto_indemnizable_neto_usd: number;
}

export interface DamageAssessmentOutput {
  numero_reclamo: string;
  numero_poliza?: string;
  imagen_analizada: string;
  modelo_deep_learning: string;
  gravedad_global: 'LEVE' | 'MEDIA' | 'GRAVE' | 'PÉRDIDA_TOTAL';
  score_danos_global: number;
  piezas_averiadas: DetectedPart[];
  liquidacion_financiera: FinancialSettlement;
  lidar_telemetria: {
    puntos_voxel_retorno?: string;
    delta_profundidad_mm?: string;
    sensor_id?: string;
    [key: string]: any;
  };
  estres_termico: {
    estres_chasis_torsional_mpa?: number;
    zona_fatiga_critica?: string;
    [key: string]: any;
  };
  keyframes?: Keyframe[];
  es_video?: boolean;
  vehiculo_intacto?: boolean;
  orientacion_detectada?: string;
  valor_comercial_vehiculo_usd?: number;
  ratio_dano_valor_comercial_pct?: number;
  es_perdida_total_50?: boolean;
  mensaje_dictamen_actuarial?: string;
  evidencias_galeria?: Array<{ id: string; url: string; label: string; ratio_dano?: number }>;
  estado_peritaje: string;
  s3_evidencia_url?: string;
  s3_foto_anotada_url?: string;
  s3_telemetria_lidar_url?: string;
  s3_dictamen_pdf_url?: string;
  s3_bucket?: string;
  s3_key_evidencia?: string;
  s3_key_dictamen?: string;
  local_dictamen_pdf_url?: string;
  timestamp: string;
}

export interface ConfirmAssessmentResponse {
  numero_reclamo: string;
  nuevo_estado: string;
  monto_aprobado_usd: number;
  mensaje: string;
  persistencia_mongo_id?: string;
  timestamp: string;
}
