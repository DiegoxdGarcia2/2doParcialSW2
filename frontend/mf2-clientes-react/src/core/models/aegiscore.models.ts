/**
 * =============================================================================
 *  AegisCore AI — Modelos e Interfaces TypeScript (Perfil A: CU01 a CU05, CU10)
 *  Alineados 100% con el contrato congelado contracts/supergraph.graphql
 * =============================================================================
 */

export type TipoPlan = 'VEHICULAR' | 'SALUD' | 'VIDA' | 'HOGAR';
export type EstadoPoliza = 'COTIZADA' | 'EMITIDA' | 'ACTIVA' | 'SUSPENDIDA' | 'VENCIDA' | 'CANCELADA';
export type CanalVenta = 'WEB_REACT' | 'WHATSAPP_N8N' | 'OFICINA_ANGULAR' | 'BROKER';
export type RolSSO = 'ADMIN' | 'AJUSTADOR' | 'PERITO' | 'ACTUARIO' | 'CLIENTE';

export interface Cliente {
  id: string;
  usuarioId?: string | null;
  tipoDocumento: string;
  numeroDocumento: string;
  nombres: string;
  apellidos: string;
  nombreCompleto: string;
  email: string;
  telefono: string;
  direccion?: string | null;
  ciudad?: string;
  scoreCrediticio?: number;
  perfilRiesgo?: string;
  createdAt: string;
}

export interface Cobertura {
  id: string;
  planId: string;
  codigo: string;
  nombre: string;
  descripcion?: string | null;
  sumaAseguradaMax: number;
  deducibleMinimo: number;
  deduciblePorcentaje: number;
  obligatoria: boolean;
}

export interface PlanSeguro {
  id: string;
  codigo: string;
  nombre: string;
  tipo: TipoPlan;
  descripcion?: string | null;
  primaBaseAnual: number;
  deducibleBasePorcentaje: number;
  activo: boolean;
  coberturas: Cobertura[];
}

export interface BienAseguradoVehiculo {
  placa: string;
  vin: string;
  marca: string;
  modelo: string;
  anio: number;
  color?: string;
  valorComercial: number;
}

export interface FacturaNotaVenta {
  id: string;
  numeroFactura: string;
  polizaId: string;
  clienteId: string;
  tipoComprobante: 'FACTURA' | 'NOTA_VENTA';
  fechaEmision: string;
  subtotal: number;
  impuestos: number;
  total: number;
  moneda: string;
  estado: 'EMITIDA' | 'PAGADA' | 'ANULADA';
  urlPdfAlmacenado?: string | null;
  hashDigitalSha256?: string | null;
}

export interface ExpedienteSiniestro {
  id: string;
  numeroReclamo: string;
  polizaId: string;
  numeroPoliza: string;
  estado: string;
  tipoSiniestro: string;
  descripcion?: string;
  canalOrigen: string;
  idempotencyKey?: string;
  ubicacionTexto?: string;
  triajeIa?: {
    gravedad: string;
    scoreDanos: number;
    piezasDetectadas: string[];
    modeloInferencia: string;
  };
  peritajeCampo?: {
    peritoId: string;
    peritoNombre: string;
    fechaInspeccion: string;
    ocrPlacaDetectada?: string;
    coincideConPoliza: boolean;
    agenteTfliteValido: boolean;
    notas?: string;
  };
  fotosEvidencia?: Array<{
    url: string;
    categoria: string;
    nitidezScore: number;
    esValidoTfJs: boolean;
    timestamp?: string;
  }>;
  montoEstimadoReparacion?: number;
  montoIndemnizacionAprobado?: number;
  deducibleCalculado?: number;
  createdAt: string;
}

export interface Poliza {
  id: string;
  numeroPoliza: string;
  cliente?: Cliente;
  plan?: PlanSeguro;
  estado: EstadoPoliza;
  fechaEmision?: string;
  fechaInicio: string;
  fechaFin: string;
  primaAnual: number;
  primaMensual: number;
  moneda: string;
  saldoCoberturaRestante: number;
  bienAsegurado: BienAseguradoVehiculo;
  canalVenta: CanalVenta;
  facturas: FacturaNotaVenta[];
  siniestros: ExpedienteSiniestro[];
  createdAt: string;
  updatedAt: string;
}

export interface ResumenUnificadoPayload {
  cliente: Cliente;
  polizasActivas: Poliza[];
  totalSaldoCoberturaDisponible: number;
  siniestrosEnCurso: ExpedienteSiniestro[];
  pagosPendientes: FacturaNotaVenta[];
  cacheDynamoDb?: {
    table: string;
    partition_key: string;
    cache_status: string;
    latency_ms: number;
    updated_at: string;
  };
}

export interface CotizacionResultado {
  primaCalculadaAnual: number;
  primaCalculadaMensual: number;
  deduciblePorcentaje: number;
  descuentoScoreAplicado: number;
  validoHasta: string;
}

export interface ResultadoValidacionNitidezLocal {
  esValidoTfJs: boolean;
  nitidezScore: number;
  varianzaLaplaciana: number;
  brilloPromedio: number;
  contrasteScore: number;
  tiempoInferenciaMs: number;
  motorInferencia: string;
  dimensionesTensor: [number, number, number];
  ocrMetadatosExtraidos: {
    tipoDocumentoDetectado: string;
    placaORuatDetectado: string;
    bordesRectangularesValidos: boolean;
    legibilidadTextoPct: number;
  };
  tokenValidacionNitidezLocal: string;
  diagnosticoVisual: string;
}

export interface ColaSincronizacionOfflineItem {
  idempotencyKey: string;
  payloadHashSha256: string;
  operacion: 'EMITIR_POLIZA_GRAPHQL' | 'PAGO_PRIMA_QR';
  descripcion: string;
  variables: Record<string, unknown>;
  createdAt: string;
  estado: 'PENDIENTE_RED' | 'SINCRONIZADO' | 'RECHAZADO';
}

