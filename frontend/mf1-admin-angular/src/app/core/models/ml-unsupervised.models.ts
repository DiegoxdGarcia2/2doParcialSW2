/**
 * =============================================================================
 *  AegisCore AI - MF1 Angular: Modelos e Interfaces para CU13
 *  Machine Learning No Supervisado (K-Means Clustering + Isolation Forest)
 *  Trazabilidad ICONIX: Capa de Entidad / DTOs
 * =============================================================================
 */

export interface ClusterProfile {
  cluster_id: number;
  nombre: string;
  total_asegurados: number;
  porcentaje_flota: number;
  edad_media: number;
  valor_vehiculo_medio_usd: number;
  frecuencia_siniestros_anual: number;
  score_riesgo_medio: number;
  prima_recomendada_descuento: string;
}

export interface FraudAlert {
  reclamo_id: string;
  poliza_id?: string;
  monto_solicitado_usd: number;
  monto_promedio_mercado_usd: number;
  divergencia_porcentaje: number;
  score_anomalia: number;
  es_anomalo: boolean;
  nivel_criticidad: 'CRÍTICO' | 'ALTO' | 'MEDIO' | 'NORMAL';
  taller_mecanico: string;
  motivo_sospecha: string;
  estado_pago: 'PENDIENTE_REVISION' | 'CONGELADO_PREVENTIVO_SAGA' | 'AUDITADO' | 'APROBADO_FAST_TRACK';
  fecha_alerta: string;
}

export interface EvaluateClaimInput {
  reclamo_id: string;
  poliza_id: string;
  edad_conductor: number;
  tipo_vehiculo: string;
  valor_comercial_usd: number;
  monto_solicitado_usd: number;
  dias_desde_emision: number;
  historial_siniestros: number;
  taller_mecanico: string;
}

export interface FraudDashboardSummary {
  threat_index_percentage: number;
  threat_level_label: string;
  perdidas_prevenidas_usd: number;
  total_siniestros_auditados: number;
  total_alertas_activas: number;
  silhouette_score_kmeans: number;
  clusters_kmeans: ClusterProfile[];
  alertas_recientes: FraudAlert[];
  timestamp: string;
}

export interface FreezeClaimResponse {
  reclamo_id: string;
  estado_anterior: string;
  nuevo_estado: string;
  score_anomalia: number;
  mensaje: string;
  persistencia_mongo_id?: string;
  timestamp: string;
}
