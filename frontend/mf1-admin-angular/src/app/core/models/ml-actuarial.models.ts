/**
 * =============================================================================
 *  AegisCore AI - MF1 Angular: Modelos e Interfaces para CU12 (Random Forest)
 *  Trazabilidad ICONIX: Capa de Entidad / DTOs
 * =============================================================================
 */

export interface PredictionInput {
  edad_asegurado: number;
  antiguedad_licencia_anios: number;
  tipo_vehiculo: string;
  anio_vehiculo: number;
  valor_comercial_usd: number;
  historial_siniestros_previos: number;
  perfil_riesgo_score: number;
  meses_a_proyectar: number;
}

export interface MonthlyProjection {
  mes: string;
  ventas_estimadas_polizas: number;
  prima_sugerida_usd: number;
  intervalo_confianza_min: number;
  intervalo_confianza_max: number;
}

export interface FeatureImportance {
  variable: string;
  importancia_porcentaje: number;
}

export interface ModelMetrics {
  r2_score: number;
  mae_usd: number;
  rmse_usd: number;
  accuracy_siniestros: number;
  total_registros_entrenamiento: number;
  n_estimadores: number;
  feature_importances: FeatureImportance[];
  fecha_ultimo_entrenamiento: string;
}

export interface PredictionOutput {
  prima_anual_optima_usd: number;
  rango_confianza_95: [number, number];
  desviacion_estandar_usd: number;
  probabilidad_siniestro_pct: number;
  nivel_riesgo_clasificado: 'BAJO' | 'MEDIO' | 'ALTO' | 'CRÍTICO';
  costo_siniestro_estimado_usd: number;
  proyecciones_mensuales: MonthlyProjection[];
  metricas_modelo: ModelMetrics;
}

export interface RetrainResponse {
  mensaje: string;
  registros_cargados: number;
  r2_score_nuevo: number;
  mae_usd_nuevo: number;
  tiempo_ejecucion_segundos: number;
  fecha_entrenamiento: string;
}
