/**
 * =============================================================================
 *  AegisCore AI - MF1 Angular: Modelos e Interfaces para CU14
 *  Monitoreo de Siniestros Estancados y Liquidez con Agente Autónomo (LangGraph)
 *  Trazabilidad ICONIX: Capa de Entidad / DTOs
 * =============================================================================
 */

export interface AgentNodeStatus {
  nodo_id: string;
  nombre: string;
  estado: string;
  latencia_ms: number;
  completado: boolean;
  descripcion?: string;
}

export interface ActiveMicroAgent {
  agente_id: string;
  nombre: string;
  rol: string;
  kafka_topic: string;
  estado: string;
  skill_primaria: string;
  latencia_actual_ms: number;
}

export interface StalledClaim {
  numero_reclamo: string;
  numero_poliza: string;
  estado_actual: string;
  dias_estancado: number;
  cuello_botella: string;
  accion_sugerida: string;
  modelo_vehiculo?: string;
  monto_estimado_usd: number;
  score_fraude: number;
}

export interface LiquidityMetrics {
  reserva_capital_total_usd: number;
  compromisos_activos_usd: number;
  reserva_remanente_usd: number;
  ratio_cobertura_pct: number;
  estado_solvencia: 'SOLVENTE' | 'ALERTA_PREVENTIVA' | 'CRITICO';
  umbral_minimo_pct: number;
}

export interface AgentClusterState {
  cluster_estado: string;
  salud_cluster_pct: number;
  latencia_promedio_ms: number;
  kafka_broker: string;
  dag_estado: string;
  nodos_grafo: AgentNodeStatus[];
  micro_agentes: ActiveMicroAgent[];
  siniestros_estancados: StalledClaim[];
  metricas_liquidez: LiquidityMetrics;
  ultima_reflexion: string;
  timestamp: string;
}

export interface RunCycleResponse {
  ciclo_id: string;
  estado_ejecucion: string;
  duracion_total_ms: number;
  nodos_visitados: string[];
  siniestros_evaluados: number;
  skills_sugeridas: number;
  reflexion_final: string;
  bitacora_id: string;
  timestamp: string;
}

export interface ExecuteSkillRequest {
  numero_reclamo: string;
  skill_id: string;
  motivo?: string;
}

export interface ExecuteSkillResponse {
  exito: boolean;
  numero_reclamo: string;
  skill_ejecutada: string;
  nuevo_estado_expediente: string;
  detalle: string;
  bitacora_id: string;
  timestamp: string;
}

export interface AgentLogEvent {
  evento_id: string;
  timestamp: string;
  nodo: string;
  tipo_evento: string;
  detalle: string;
  impacto_expedientes: number;
}
