/**
 * =============================================================================
 *  AegisCore AI - MF1 Angular: [ENTITY] Modelos de Siniestralidad y Riesgo 360°
 *  Metodología ICONIX - Contratos de Datos para Siniestralidad Real PostgreSQL
 * =============================================================================
 */

export type TipoVehiculoTipo = 'TODOS' | 'SUV' | 'CAMIONETA' | 'HATCHBACK' | 'MOTOCICLETA' | 'SEDAN';
export type RangoEdadTipo = 'TODOS' | '18-25' | '26-35' | '36-50' | '51-65' | '65+';
export type AntiguedadLicenciaTipo = 'TODOS' | 'NOVATO' | 'INTERMEDIO' | 'EXPERTO';
export type AntiguedadVehiculoTipo = 'TODOS' | '2020_2023' | '2015_2019' | '2010_2014';

export interface ActuarialLossFilterInput {
  tipo_vehiculo: TipoVehiculoTipo;
  rango_edad: RangoEdadTipo;
  antiguedad_licencia: AntiguedadLicenciaTipo;
  antiguedad_vehiculo: AntiguedadVehiculoTipo;
}

export interface VehicleLossMetric {
  tipo_vehiculo: string;
  total_polizas: number;
  siniestros_count: number;
  frecuencia_siniestralidad_pct: number;
  costo_medio_usd: number;
  prima_media_usd: number;
  total_costo_siniestros_usd: number;
  total_primas_usd: number;
  loss_ratio_pct: number;
  semaforo_tecnico: string;
}

export interface AgeCohortMetric {
  rango_edad: string;
  total_conductores: number;
  total_siniestros: number;
  frecuencia_pct: number;
  costo_medio_usd: number;
}

export interface MonthlyTrendMetric {
  mes: string;
  polizas_activas: number;
  siniestros_mes: number;
  costo_total_mes_usd: number;
  tasa_incurrencia_pct: number;
}

export interface ActuarialLossSummary {
  frecuencia_siniestralidad_pct: number;
  severidad_media_usd: number;
  loss_ratio_tecnico_pct: number;
  prima_media_anual_usd: number;
  score_medio_riesgo: number;
  total_polizas: number;
  total_siniestros: number;
  costo_total_siniestros_usd: number;
  primas_totales_usd: number;
  salud_cartera_label: string;
  desglose_por_vehiculo: VehicleLossMetric[];
  cohortes_edad: AgeCohortMetric[];
  tendencia_mensual: MonthlyTrendMetric[];
  filtros_aplicados: ActuarialLossFilterInput;
  timestamp: string;
}

export interface FilterOptionItem {
  id: string;
  label: string;
}

export interface ActuarialFilterOptions {
  tipos_vehiculo: FilterOptionItem[];
  rangos_edad: FilterOptionItem[];
  antiguedades_licencia: FilterOptionItem[];
  antiguedades_vehiculo: FilterOptionItem[];
}

