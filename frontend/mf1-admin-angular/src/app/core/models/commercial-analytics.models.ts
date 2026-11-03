/**
 * =============================================================================
 *  AegisCore AI - MF1 Angular: [ENTITY] Modelos de Analítica Comercial 360°
 *  Metodología ICONIX - Contratos de Datos y Tipos para Rentabilidad y Canales
 * =============================================================================
 */

export type DepartamentoTipo = 'TODOS' | 'SANTA_CRUZ' | 'LA_PAZ' | 'COCHABAMBA' | 'TARIJA' | 'CHUQUISACA' | 'ORURO' | 'POTOSI' | 'BENI' | 'PANDO';
export type RamoTipo = 'TODOS' | 'VEHICULAR' | 'SALUD' | 'VIDA' | 'HOGAR';
export type CanalVentaTipo = 'TODOS' | 'WEB_REACT' | 'WHATSAPP_N8N' | 'BROKER' | 'OFICINA_ANGULAR';
export type PeriodoTipo = 'Q1' | 'Q2' | 'Q3' | 'Q4' | 'YTD' | 'MENSUAL';

export interface CommercialFilterInput {
  departamento: DepartamentoTipo;
  ramo: RamoTipo;
  canal: CanalVentaTipo;
  periodo: PeriodoTipo;
}

export interface ChannelEfficiency {
  canal: string;
  codigo_canal: string;
  cac_usd: number;
  conversion_pct: number;
  polizas_vendidas: number;
  ingresos_usd: number;
  margen_contribucion_pct: number;
}

export interface LtvRetentionTrend {
  mes: string;
  ltv_usd: number;
  retencion_pct: number;
  churn_pct: number;
}

export interface CommercialKpiSummary {
  prima_media_usd: number;
  cac_promedio_usd: number;
  ltv_promedio_usd: number;
  ltv_cac_ratio: number;
  churn_anual_pct: number;
  retencion_anual_pct: number;
  tasa_conversion_global_pct: number;
  polizas_totales: number;
  ingresos_totales_usd: number;
  salud_comercial_label: string;
  canales_eficiencia: ChannelEfficiency[];
  tendencia_mensual: LtvRetentionTrend[];
  filtros_aplicados: CommercialFilterInput;
  timestamp: string;
}

export interface FilterOptionItem {
  id: string;
  label: string;
}

export interface FilterOptions {
  departamentos: FilterOptionItem[];
  ramos: FilterOptionItem[];
  canales: FilterOptionItem[];
  periodos: FilterOptionItem[];
}

