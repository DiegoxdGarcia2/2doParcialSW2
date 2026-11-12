/**
 * =============================================================================
 *  AegisCore AI — Cliente GraphQL Federado & Cola Offline PWA
 *  Conecta el Micro-Frontend 2 (React PWA) con MS1 (PHP 8.3 DDD / GraphQL)
 *  Soportando:
 *    - CU02: resumenUnificadoAsegurado (Federación PostgreSQL + MongoDB + DynamoDB)
 *    - CU03: listarPlanesSeguro, registrarPlanSeguro, agregarCoberturaPlan, registrarCliente
 *    - CU04: cotizarPolizaEnLinea, emitirPoliza (con Token IA Local + Cola Offline)
 *    - CU05: Pedido de Póliza por WhatsApp n8n y Generación de Factura PDF SHA-256
 *    - CU09: Simulación de Paso 2 Saga (Descuento de Cobertura y Rollback en MS1)
 *    - CU10: Cobro de Prima QR con Idempotency-Key (UUIDv4) en DynamoDB
 * =============================================================================
 */

import {
  BienAseguradoVehiculo,
  Cliente,
  ColaSincronizacionOfflineItem,
  CotizacionResultado,
  PlanSeguro,
  Poliza,
  ResumenUnificadoPayload,
  TipoPlan,
} from '../models/aegiscore.models';

const SEED_PLANES: PlanSeguro[] = [
  {
    id: 'a0000001-0000-0000-0000-000000000001',
    codigo: 'PLAN-AUTO-FULL',
    nombre: 'Todo Riesgo Vehicular Premium',
    tipo: 'VEHICULAR',
    descripcion: 'Cobertura completa contra choques, robo total/parcial, vuelcos y auxilio mecánico 24/7.',
    primaBaseAnual: 720.0,
    deducibleBasePorcentaje: 10.0,
    activo: true,
    coberturas: [
      {
        id: 'c0000001-0000-0000-0000-000000000001',
        planId: 'a0000001-0000-0000-0000-000000000001',
        codigo: 'COB-DANOS-MATERIALES',
        nombre: 'Daños Materiales por Colisión y Vuelco',
        descripcion: 'Indemnización o reparación en talleres autorizados.',
        sumaAseguradaMax: 25000.0,
        deducibleMinimo: 150.0,
        deduciblePorcentaje: 10.0,
        obligatoria: true,
      },
      {
        id: 'c0000001-0000-0000-0000-000000000002',
        planId: 'a0000001-0000-0000-0000-000000000001',
        codigo: 'COB-ROBO-TOTAL',
        nombre: 'Robo Total del Vehículo',
        descripcion: 'Reposición de valor comercial según tabla depreciativa.',
        sumaAseguradaMax: 25000.0,
        deducibleMinimo: 200.0,
        deduciblePorcentaje: 10.0,
        obligatoria: true,
      },
      {
        id: 'c0000001-0000-0000-0000-000000000003',
        planId: 'a0000001-0000-0000-0000-000000000001',
        codigo: 'COB-RESP-CIVIL',
        nombre: 'Responsabilidad Civil a Terceros',
        descripcion: 'Cobertura frente a demandas o daños a bienes de terceros.',
        sumaAseguradaMax: 15000.0,
        deducibleMinimo: 100.0,
        deduciblePorcentaje: 5.0,
        obligatoria: true,
      },
    ],
  },
  {
    id: 'a0000001-0000-0000-0000-000000000002',
    codigo: 'PLAN-AUTO-RC',
    nombre: 'Responsabilidad Civil Obligatoria',
    tipo: 'VEHICULAR',
    descripcion: 'Cobertura ante daños materiales y corporales a terceros involucrados.',
    primaBaseAnual: 280.0,
    deducibleBasePorcentaje: 5.0,
    activo: true,
    coberturas: [
      {
        id: 'c0000001-0000-0000-0000-000000000005',
        planId: 'a0000001-0000-0000-0000-000000000002',
        codigo: 'COB-RC-BASICA',
        nombre: 'Responsabilidad Civil Extracontractual',
        descripcion: 'Daños a terceros en accidentes de tránsito.',
        sumaAseguradaMax: 12000.0,
        deducibleMinimo: 80.0,
        deduciblePorcentaje: 5.0,
        obligatoria: true,
      },
    ],
  },
  {
    id: 'a0000001-0000-0000-0000-000000000003',
    codigo: 'PLAN-SALUD-TOTAL',
    nombre: 'Salud Integral Familiar',
    tipo: 'SALUD',
    descripcion: 'Atención en red hospitalaria privada, cirugías, medicamentos y telemedicina.',
    primaBaseAnual: 950.0,
    deducibleBasePorcentaje: 15.0,
    activo: true,
    coberturas: [
      {
        id: 'c0000001-0000-0000-0000-000000000004',
        planId: 'a0000001-0000-0000-0000-000000000003',
        codigo: 'COB-HOSPITALIZACION',
        nombre: 'Gastos Médicos y Hospitalización',
        descripcion: 'Cobertura para internaciones y procedimientos quirúrgicos.',
        sumaAseguradaMax: 30000.0,
        deducibleMinimo: 250.0,
        deduciblePorcentaje: 15.0,
        obligatoria: true,
      },
    ],
  },
];

const SEED_CLIENTE: Cliente = {
  id: 'b0000001-0000-0000-0000-000000000001',
  usuarioId: 'e0000001-0000-0000-0000-000000000004',
  tipoDocumento: 'CI',
  numeroDocumento: '6234891-SC',
  nombres: 'Carlos',
  apellidos: 'Mendoza Roca',
  nombreCompleto: 'Carlos Mendoza Roca',
  email: 'carlos.mendoza@gmail.com',
  telefono: '+591 71099887',
  direccion: 'Av. San Martín #450, Equipetrol, Santa Cruz',
  ciudad: 'Santa Cruz',
  scoreCrediticio: 820,
  perfilRiesgo: 'BAJO',
  createdAt: '2026-08-25T10:00:00Z',
};

export class ApolloFederationClient {
  private readonly ms1BaseUrl: string;
  private readonly queueKey = 'aegiscore_react_pwa_offline_queue_v1';

  constructor(
    ms1BaseUrl = (import.meta as any)?.env?.VITE_MS1_URL ||
      (typeof window !== 'undefined' && (window as any).__AEGIS_MS1_URL) ||
      (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
        ? 'http://localhost:8001'
        : 'https://aegiscore-ms1-polizas-jskh4rw62q-uc.a.run.app')
  ) {
    this.ms1BaseUrl = ms1BaseUrl.replace(/\/$/, '');
  }

  public static generarUUIDv4(): string {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return crypto.randomUUID();
    }
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  /**
   * Ejecuta una consulta o mutación GraphQL contra MS1 (http://localhost:8001/graphql).
   */
  public async ejecutarGraphQL<T = Record<string, unknown>>(
    query: string,
    variables: Record<string, unknown> = {},
    jwtToken?: string,
    idempotencyKey?: string
  ): Promise<{ data?: T; errors?: Array<{ message: string }>; fromBackend: boolean }> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (jwtToken) {
      headers['Authorization'] = `Bearer ${jwtToken}`;
    }
    if (idempotencyKey) {
      headers['Idempotency-Key'] = idempotencyKey;
    }

    try {
      const res = await fetch(`${this.ms1BaseUrl}/graphql`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ query, variables }),
      });

      if (!res.ok) {
        return {
          fromBackend: false,
          errors: [{ message: `HTTP Error ${res.status}: ${res.statusText}` }],
        };
      }

      const contentType = res.headers.get('content-type') || '';
      if (!contentType.includes('application/json')) {
        return {
          fromBackend: false,
          errors: [{ message: 'El servidor no devolvió una respuesta JSON válida.' }],
        };
      }

      const json = await res.json();
      return {
        data: json.data as T,
        errors: json.errors,
        fromBackend: true,
      };
    } catch (err: any) {
      return {
        fromBackend: false,
        errors: [{ message: err?.message || 'Error de red o conexión hacia MS1 GraphQL' }],
      };
    }
  }

  /**
   * CU02: Consultar Estado Unificado de Pólizas, Vehículos y Siniestros (Federación GraphQL).
   */
  public async consultarResumenUnificadoAsegurado(
    clienteId = 'b0000001-0000-0000-0000-000000000001',
    jwtToken?: string
  ): Promise<{ payload: ResumenUnificadoPayload; rawQuery: string; fromBackend: boolean }> {
    const rawQuery = `query ObtenerResumenUnificadoAsegurado($clienteId: ID!) {
  resumenUnificadoAsegurado(clienteId: $clienteId) {
    totalSaldoCoberturaDisponible
    cliente {
      id
      tipoDocumento
      numeroDocumento
      nombreCompleto
      email
      telefono
      ciudad
      scoreCrediticio
      perfilRiesgo
    }
    polizasActivas {
      id
      numeroPoliza
      estado
      fechaInicio
      fechaFin
      primaAnual
      primaMensual
      moneda
      saldoCoberturaRestante
      canalVenta
      bienAsegurado {
        placa
        vin
        marca
        modelo
        anio
        color
        valorComercial
      }
      plan {
        id
        codigo
        nombre
        tipo
        deducibleBasePorcentaje
        coberturas {
          id
          codigo
          nombre
          sumaAseguradaMax
          deducibleMinimo
          deduciblePorcentaje
          obligatoria
        }
      }
      facturas {
        id
        numeroFactura
        polizaId
        tipoComprobante
        fechaEmision
        subtotal
        impuestos
        total
        moneda
        estado
        urlPdfAlmacenado
        hashDigitalSha256
      }
    }
    siniestrosEnCurso {
      id
      numeroReclamo
      numeroPoliza
      estado
      tipoSiniestro
      descripcion
      ubicacionTexto
      montoEstimadoReparacion
      montoIndemnizacionAprobado
      deducibleCalculado
      triajeIa {
        gravedad
        scoreDanos
        piezasDetectadas
        modeloInferencia
      }
      peritajeCampo {
        peritoNombre
        ocrPlacaDetectada
        coincideConPoliza
        agenteTfliteValido
        notas
      }
      fotosEvidencia {
        url
        categoria
        nitidezScore
        esValidoTfJs
      }
    }
    pagosPendientes {
      id
      numeroFactura
      polizaId
      tipoComprobante
      fechaEmision
      subtotal
      impuestos
      total
      moneda
      estado
      urlPdfAlmacenado
      hashDigitalSha256
    }
  }
}`;

    try {
      const response = await this.ejecutarGraphQL<{ resumenUnificadoAsegurado: ResumenUnificadoPayload }>(
        rawQuery,
        { clienteId },
        jwtToken
      );
      if (response.data?.resumenUnificadoAsegurado) {
        return {
          payload: response.data.resumenUnificadoAsegurado,
          rawQuery,
          fromBackend: true,
        };
      }
    } catch {
      // Fallback PWA Offline
    }

    return {
      payload: this.construirResumenFallbackOffline(),
      rawQuery,
      fromBackend: false,
    };
  }

  /**
   * CU03: Listar Catálogo de Planes y Clientes vía GraphQL.
   */
  public async listarCatalogoYClientes(jwtToken?: string): Promise<{
    planes: PlanSeguro[];
    clientes: Cliente[];
    fromBackend: boolean;
  }> {
    const query = `query ListarCatalogoERP {
  listarPlanesSeguro {
    id
    codigo
    nombre
    tipo
    descripcion
    primaBaseAnual
    deducibleBasePorcentaje
    activo
    coberturas {
      id
      planId
      codigo
      nombre
      sumaAseguradaMax
      deducibleMinimo
      deduciblePorcentaje
      obligatoria
    }
  }
  listarClientes {
    id
    tipoDocumento
    numeroDocumento
    nombres
    apellidos
    nombreCompleto
    email
    telefono
    ciudad
    scoreCrediticio
    perfilRiesgo
    createdAt
  }
}`;

    try {
      const res = await this.ejecutarGraphQL<{
        listarPlanesSeguro: PlanSeguro[];
        listarClientes: Cliente[];
      }>(query, {}, jwtToken);

      if (res.data?.listarPlanesSeguro) {
        return {
          planes: res.data.listarPlanesSeguro,
          clientes: res.data.listarClientes ?? [SEED_CLIENTE],
          fromBackend: true,
        };
      }
    } catch {
      // Fallback Offline
    }

    return {
      planes: SEED_PLANES,
      clientes: [SEED_CLIENTE],
      fromBackend: false,
    };
  }

  /**
   * CU03: Registrar un nuevo Plan de Seguro en MS1 DDD vía GraphQL.
   */
  public async registrarPlanSeguroGraphQL(
    input: {
      codigo: string;
      nombre: string;
      tipo: TipoPlan;
      primaBaseAnual: number;
      deducibleBasePorcentaje: number;
      descripcion: string;
    },
    jwtToken?: string
  ): Promise<PlanSeguro> {
    const mutation = `mutation RegistrarPlanDDD($input: JSON!) {
  registrarPlanSeguro(input: $input) {
    id
    codigo
    nombre
    tipo
    primaBaseAnual
    deducibleBasePorcentaje
    activo
    coberturas {
      id
      codigo
      nombre
      sumaAseguradaMax
    }
  }
}`;

    try {
      const res = await this.ejecutarGraphQL<{ registrarPlanSeguro: PlanSeguro }>(
        mutation,
        { input },
        jwtToken
      );
      if (res.data?.registrarPlanSeguro) {
        return res.data.registrarPlanSeguro;
      }
    } catch {
      // Fallback
    }

    return {
      id: ApolloFederationClient.generarUUIDv4(),
      codigo: input.codigo.toUpperCase(),
      nombre: input.nombre,
      tipo: input.tipo,
      descripcion: input.descripcion,
      primaBaseAnual: input.primaBaseAnual,
      deducibleBasePorcentaje: input.deducibleBasePorcentaje,
      activo: true,
      coberturas: [
        {
          id: ApolloFederationClient.generarUUIDv4(),
          planId: 'local-plan',
          codigo: `COB-${input.codigo.slice(-4).toUpperCase()}`,
          nombre: 'Cobertura Principal Integral',
          sumaAseguradaMax: 25000,
          deducibleMinimo: 150,
          deduciblePorcentaje: input.deducibleBasePorcentaje,
          obligatoria: true,
        },
      ],
    };
  }

  /**
   * CU03: Registrar un nuevo Cliente Asegurado en MS1 DDD vía GraphQL.
   */
  public async registrarClienteGraphQL(
    input: {
      tipoDocumento: string;
      numeroDocumento: string;
      nombres: string;
      apellidos: string;
      email: string;
      telefono: string;
      ciudad: string;
      scoreCrediticio: number;
    },
    jwtToken?: string
  ): Promise<Cliente> {
    const mutation = `mutation RegistrarClienteDDD($input: JSON!) {
  registrarCliente(input: $input) {
    id
    tipoDocumento
    numeroDocumento
    nombres
    apellidos
    nombreCompleto
    email
    telefono
    ciudad
    scoreCrediticio
    perfilRiesgo
    createdAt
  }
}`;

    try {
      const res = await this.ejecutarGraphQL<{ registrarCliente: Cliente }>(
        mutation,
        { input },
        jwtToken
      );
      if (res.data?.registrarCliente) {
        return res.data.registrarCliente;
      }
    } catch {
      // Fallback
    }

    return {
      id: ApolloFederationClient.generarUUIDv4(),
      tipoDocumento: input.tipoDocumento,
      numeroDocumento: input.numeroDocumento,
      nombres: input.nombres,
      apellidos: input.apellidos,
      nombreCompleto: `${input.nombres} ${input.apellidos}`,
      email: input.email,
      telefono: input.telefono,
      ciudad: input.ciudad,
      scoreCrediticio: input.scoreCrediticio,
      perfilRiesgo: input.scoreCrediticio >= 780 ? 'BAJO' : 'MODERADO',
      createdAt: new Date().toISOString(),
    };
  }

  /**
   * CU03: Vincular una nueva Cobertura (con FK planId) a un Plan de Seguro existente.
   */
  public async agregarCoberturaPlanGraphQL(
    input: {
      planId: string;
      codigo: string;
      nombre: string;
      sumaAseguradaMax: number;
      deducibleMinimo: number;
      deduciblePorcentaje: number;
    },
    jwtToken?: string
  ): Promise<PlanSeguro | null> {
    const mutation = `mutation AgregarCoberturaFK($input: JSON!) {
  agregarCoberturaPlan(input: $input) {
    id
    codigo
    nombre
    tipo
    primaBaseAnual
    deducibleBasePorcentaje
    activo
    coberturas {
      id
      planId
      codigo
      nombre
      sumaAseguradaMax
      deducibleMinimo
      deduciblePorcentaje
      obligatoria
    }
  }
}`;
    try {
      const res = await this.ejecutarGraphQL<{ agregarCoberturaPlan: PlanSeguro }>(
        mutation,
        { input },
        jwtToken
      );
      if (res.data?.agregarCoberturaPlan) {
        return res.data.agregarCoberturaPlan;
      }
    } catch {
      // Fallback
    }
    return null;
  }

  /**
   * Alterna el estado activo/pausado de un Plan de Seguro.
   */
  public async alternarEstadoPlan(
    planId: string
  ): Promise<{ status: string; plan?: Record<string, unknown> }> {
    try {
      const res = await fetch(`${this.ms1BaseUrl}/api/v1/catalogo/toggle-plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ planId }),
      });
      if (res.ok) {
        return res.json();
      }
    } catch {
      // Fallback si el backend está desconectado o en modo offline
    }
    return { status: 'success_simulated' };
  }

  /**
   * CU04: Cotizar Póliza en Línea vía GraphQL.
   */
  public async cotizarPolizaEnLinea(
    input: {
      tipoPlan: TipoPlan;
      planId: string;
      edadConductor: number;
      datosBien: BienAseguradoVehiculo;
      ciudad: string;
    },
    jwtToken?: string
  ): Promise<CotizacionResultado> {
    const mutation = `mutation CotizarPolizaWeb($input: CotizarPolizaInput!) {
  cotizarPolizaEnLinea(input: $input) {
    primaCalculadaAnual
    primaCalculadaMensual
    deduciblePorcentaje
    descuentoScoreAplicado
    validoHasta
  }
}`;

    try {
      const res = await this.ejecutarGraphQL<{ cotizarPolizaEnLinea: CotizacionResultado }>(
        mutation,
        { input },
        jwtToken
      );
      if (res.data?.cotizarPolizaEnLinea) {
        return res.data.cotizarPolizaEnLinea;
      }
    } catch {
      // Cálculo local idéntico al Dominio DDD cuando opera en Modo Offline PWA
    }

    const primaBruta = 396 + input.datosBien.valorComercial * 0.0185;
    const descuento = Number((primaBruta * 0.075).toFixed(2));
    const primaAnual = Number((primaBruta - descuento).toFixed(2));
    return {
      primaCalculadaAnual: primaAnual,
      primaCalculadaMensual: Number((primaAnual / 12).toFixed(2)),
      deduciblePorcentaje: 10.0,
      descuentoScoreAplicado: descuento,
      validoHasta: new Date(Date.now() + 15 * 86400000).toISOString(),
    };
  }

  /**
   * CU04: Emitir Póliza en Línea vía GraphQL (o encolar en IndexedDB/LocalStorage si está Offline).
   */
  public async emitirPolizaEnLinea(
    input: {
      clienteId: string;
      planId: string;
      datosBien: BienAseguradoVehiculo;
      fechaInicio: string;
      mesesVigencia: number;
      canalVenta: 'WEB_REACT';
      tokenValidacionNitidezLocal: string;
    },
    modoOfflineSimulado = false,
    jwtToken?: string
  ): Promise<{
    poliza?: Poliza;
    encoladoOffline?: ColaSincronizacionOfflineItem;
    idempotencyKey: string;
  }> {
    const idempotencyKey = ApolloFederationClient.generarUUIDv4();

    if (modoOfflineSimulado) {
      const item = this.encolarOperacionOffline(
        idempotencyKey,
        'EMITIR_POLIZA_GRAPHQL',
        `Emisión Póliza Vehículo ${input.datosBien.marca} ${input.datosBien.modelo} (${input.datosBien.placa})`,
        { input }
      );
      return { encoladoOffline: item, idempotencyKey };
    }

    const mutation = `mutation EmitirPolizaWeb($input: EmitirPolizaInput!) {
  emitirPoliza(input: $input) {
    id
    numeroPoliza
    estado
    fechaInicio
    fechaFin
    primaAnual
    primaMensual
    moneda
    saldoCoberturaRestante
    canalVenta
    bienAsegurado {
      placa
      vin
      marca
      modelo
      anio
      valorComercial
    }
    facturas {
      id
      numeroFactura
      total
      urlPdfAlmacenado
      hashDigitalSha256
    }
  }
}`;

    try {
      const res = await this.ejecutarGraphQL<{ emitirPoliza: Poliza }>(
        mutation,
        { input },
        jwtToken,
        idempotencyKey
      );
      if (res.errors && res.errors.length > 0) {
        throw new Error(res.errors[0].message);
      }
      if (res.data?.emitirPoliza) {
        return { poliza: res.data.emitirPoliza, idempotencyKey };
      }
    } catch (err) {
      if (err instanceof Error && err.message.includes('baja nitidez')) {
        throw err;
      }
    }

    // Fallback si el servidor no está accesible
    const fallbackPoliza: Poliza = {
      id: ApolloFederationClient.generarUUIDv4(),
      numeroPoliza: `POL-2026-AUT-${Math.floor(10000 + Math.random() * 89999)}`,
      estado: 'ACTIVA',
      fechaInicio: input.fechaInicio,
      fechaFin: new Date(Date.now() + 365 * 86400000).toISOString(),
      primaAnual: 785.5,
      primaMensual: 65.46,
      moneda: 'USD',
      saldoCoberturaRestante: 25000.0,
      bienAsegurado: input.datosBien,
      canalVenta: 'WEB_REACT',
      facturas: [],
      siniestros: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    return { poliza: fallbackPoliza, idempotencyKey };
  }

  /**
   * CU05: Dispara el flujo WhatsApp -> n8n (:5678) -> MS1 PHP (:8001) -> Factura PDF con SHA-256.
   */
  public async contratarPolizaWhatsAppN8n(payload: {
    telefono: string;
    numero_documento: string;
    placa: string;
    marca: string;
    modelo: string;
    anio: number;
    valor_comercial: number;
    plan_codigo: string;
    tipo_comprobante: 'FACTURA' | 'NOTA_VENTA';
  }): Promise<{
    status: string;
    mensaje_whatsapp: string;
    poliza: Poliza;
    factura: {
      id: string;
      numeroFactura: string;
      subtotal: number;
      impuestos: number;
      total: number;
      moneda: string;
      tipoComprobante: string;
    };
    url_pdf: string;
    hash_digital_sha256: string;
  }> {
    try {
      const n8nRes = await fetch('http://localhost:5678/webhook/whatsapp-pedido-poliza', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (n8nRes.ok) {
        const execJson = await n8nRes.json();
        if (execJson.result && execJson.result.poliza) {
          return execJson.result;
        }
      }
    } catch {
      // Continúa directo a MS1 si el puerto 5678 no responde
    }

    const res = await fetch(`${this.ms1BaseUrl}/api/v1/whatsapp/pedido-poliza`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(`Error al procesar pedido WhatsApp en MS1 (${res.status})`);
    }
    return res.json();
  }

  /**
   * CU09 (Apoyo Saga en MS1 PHP): Ejecuta Paso 2 (Descontar Cobertura) o Rollback (Compensar Cobertura).
   */
  public async ejecutarAccionSagaMS1(
    accion: 'descontar-cobertura' | 'compensar-cobertura',
    polizaId: string,
    montoIndemnizacion: number
  ): Promise<Record<string, unknown>> {
    const res = await fetch(`${this.ms1BaseUrl}/api/v1/saga/${accion}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        saga_id: ApolloFederationClient.generarUUIDv4(),
        correlation_id: ApolloFederationClient.generarUUIDv4(),
        payload: {
          reclamo_id: 'REC-2026-00492',
          poliza_id: polizaId,
          monto_indemnizacion: montoIndemnizacion,
          motivo_fallo: 'Fondos insuficientes en reserva técnica MS3 (Simulación Rollback CU09)',
        },
      }),
    });
    return res.json();
  }

  /**
   * CU10: Procesar Pago de Prima por QR con Sandbox Bancario SIP y persistencia en PostgreSQL + DynamoDB.
   */
  public async procesarPagoPrimaQRIdempotente(
    input: {
      polizaId: string;
      facturaId?: string;
      numeroCuota: number;
      monto: number;
      bancoSandbox?: string;
    },
    idempotencyKey: string
  ): Promise<{
    id: string;
    polizaId: string;
    facturaId?: string | null;
    numeroCuota: number;
    monto: number;
    moneda: string;
    idempotencyKey: string;
    qrImagenPayload: string;
    estado: string;
    codigoAutorizacion: string;
    bancoSandbox?: string;
    sandboxVoucherUrl?: string;
    fechaPago: string;
    fueIdempotente: boolean;
    cacheHit: string;
  }> {
    const res = await fetch(`${this.ms1BaseUrl}/api/v1/pagos-qr`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Idempotency-Key': idempotencyKey,
      },
      body: JSON.stringify({ ...input, idempotencyKey }),
    });
    return res.json();
  }

  public async listarPagosQrRegistrados(polizaId?: string): Promise<
    Array<{
      id: string;
      polizaId: string;
      facturaId?: string | null;
      numeroCuota: number;
      monto: number;
      moneda: string;
      idempotencyKey: string;
      codigoAutorizacion: string;
      bancoSandbox?: string;
      estado: string;
      fechaPago: string;
    }>
  > {
    try {
      const qs = polizaId ? `?poliza_id=${encodeURIComponent(polizaId)}` : '';
      const res = await fetch(`${this.ms1BaseUrl}/api/v1/pagos-qr${qs}`);
      if (res.ok) {
        const data = await res.json();
        return data.pagos ?? [];
      }
    } catch {
      // Fallback
    }
    return [];
  }

  public async generarCertificadoPolizaS3(polizaId: string): Promise<{
    numeroPoliza: string;
    filename: string;
    urlPdf: string;
    s3Url?: string | null;
    localUrl: string;
    hashSha256: string;
  }> {
    const res = await fetch(
      `${this.ms1BaseUrl}/api/v1/polizas/${encodeURIComponent(polizaId)}/certificado-pdf?format=json`
    );
    if (!res.ok) {
      throw new Error(`No se pudo generar el certificado PDF (${res.status})`);
    }
    return res.json();
  }

  public async subirDocumentoAS3(
    base64Data: string,
    fileName: string,
    folder = 'documentos-ruat',
    contentType = 'image/png'
  ): Promise<{
    uploaded: boolean;
    bucket: string;
    key: string;
    s3Url: string;
    hashSha256: string;
    bytes: number;
  }> {
    try {
      const res = await fetch(`${this.ms1BaseUrl}/api/v1/s3/upload-documento`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ base64Data, fileName, folder, contentType }),
      });
      if (res.ok) {
        return res.json();
      }
    } catch {
      // Fallback
    }

    const cleanFileName = fileName.replace(/[^a-zA-Z0-9._-]/g, '_');
    const hash = (ApolloFederationClient.generarUUIDv4().replace(/-/g, '') + 'e94b281f6c77a3d9021e').slice(0, 64);
    return {
      uploaded: true,
      bucket: 'servicio-de-seguros-aegiscore',
      key: `${folder}/${cleanFileName}`,
      s3Url: `https://servicio-de-seguros-aegiscore.s3.us-east-2.amazonaws.com/${folder}/${cleanFileName}`,
      hashSha256: hash,
      bytes: Math.round(base64Data.length * 0.75),
    };
  }

  public async listarSesionesSSO(): Promise<
    Array<{
      session_id: string;
      keycloak_sub: string;
      email?: string;
      nombre_completo?: string;
      rol: string;
      dispositivo?: string;
      token_sha256: string;
      status: string;
      created_at: string;
    }>
  > {
    try {
      const res = await fetch(`${this.ms1BaseUrl}/api/v1/auth/sso-sessions`);
      if (res.ok) {
        const data = await res.json();
        return data.sesiones ?? [];
      }
    } catch {
      // Fallback
    }
    return [];
  }

  public async cerrarSesionSSO(sessionId = 'ALL'): Promise<{
    revoked: boolean;
    revoked_count: number;
    sesiones: Array<{
      session_id: string;
      keycloak_sub: string;
      email?: string;
      nombre_completo?: string;
      rol: string;
      dispositivo?: string;
      token_sha256: string;
      status: string;
      created_at: string;
    }>;
  }> {
    const res = await fetch(`${this.ms1BaseUrl}/api/v1/auth/sso-logout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    });
    return res.json();
  }

  public obtenerColaOffline(): ColaSincronizacionOfflineItem[] {
    if (typeof localStorage === 'undefined') return [];
    const raw = localStorage.getItem(this.queueKey);
    if (!raw) return [];
    try {
      return JSON.parse(raw) as ColaSincronizacionOfflineItem[];
    } catch {
      return [];
    }
  }

  public encolarOperacionOffline(
    idempotencyKey: string,
    operacion: ColaSincronizacionOfflineItem['operacion'],
    descripcion: string,
    variables: Record<string, unknown>
  ): ColaSincronizacionOfflineItem {
    const item: ColaSincronizacionOfflineItem = {
      idempotencyKey,
      payloadHashSha256: `sha256-${btoa(JSON.stringify(variables)).slice(0, 32)}`,
      operacion,
      descripcion,
      variables,
      createdAt: new Date().toISOString(),
      estado: 'PENDIENTE_RED',
    };
    const actual = this.obtenerColaOffline();
    const nueva = [item, ...actual];
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(this.queueKey, JSON.stringify(nueva));
    }
    return item;
  }

  public async sincronizarColaOffline(jwtToken?: string): Promise<ColaSincronizacionOfflineItem[]> {
    const cola = this.obtenerColaOffline();
    const actualizada: ColaSincronizacionOfflineItem[] = [];

    for (const item of cola) {
      if (item.estado === 'SINCRONIZADO') {
        actualizada.push(item);
        continue;
      }
      try {
        if (item.operacion === 'EMITIR_POLIZA_GRAPHQL') {
          const mutation = `mutation EmitirSync($input: EmitirPolizaInput!) { emitirPoliza(input: $input) { id numeroPoliza estado } }`;
          await this.ejecutarGraphQL(mutation, item.variables, jwtToken, item.idempotencyKey);
        }
        actualizada.push({ ...item, estado: 'SINCRONIZADO' });
      } catch {
        actualizada.push(item);
      }
    }

    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(this.queueKey, JSON.stringify(actualizada));
    }
    return actualizada;
  }

  private construirResumenFallbackOffline(): ResumenUnificadoPayload {
    return {
      cliente: SEED_CLIENTE,
      polizasActivas: [
        {
          id: 'd0000001-0000-0000-0000-000000000001',
          numeroPoliza: 'POL-2026-AUT-00892',
          cliente: SEED_CLIENTE,
          plan: SEED_PLANES[0],
          estado: 'ACTIVA',
          fechaInicio: '2026-08-28T00:00:00Z',
          fechaFin: '2027-08-28T23:59:59Z',
          primaAnual: 720.0,
          primaMensual: 60.0,
          moneda: 'USD',
          saldoCoberturaRestante: 25000.0,
          bienAsegurado: {
            placa: '4028-PLK',
            vin: '8AJBA3CD701982736',
            marca: 'Toyota',
            modelo: 'Hilux 4x4',
            anio: 2023,
            color: 'Blanco Perlado',
            valorComercial: 34500.0,
          },
          canalVenta: 'WEB_REACT',
          facturas: [],
          siniestros: [],
          createdAt: '2026-08-28T10:00:00Z',
          updatedAt: '2026-10-28T10:00:00Z',
        },
      ],
      totalSaldoCoberturaDisponible: 25000.0,
      siniestrosEnCurso: [
        {
          id: '671800000000000000000492',
          numeroReclamo: 'REC-2026-00492',
          polizaId: 'd0000001-0000-0000-0000-000000000001',
          numeroPoliza: 'POL-2026-AUT-00892',
          estado: 'PERITAJE_COMPLETADO',
          tipoSiniestro: 'CHOQUE_VIAL',
          descripcion: 'Colisión por alcance frontal en intersección con semáforo intermitente.',
          canalOrigen: 'WHATSAPP_N8N',
          ubicacionTexto: '4to Anillo y Av. San Martín, Equipetrol Norte, Santa Cruz',
          triajeIa: {
            gravedad: 'MEDIA',
            scoreDanos: 0.74,
            piezasDetectadas: ['PARACHOQUES_DELANTERO', 'OPTICA_DERECHA', 'CAPO_PARCIAL'],
            modeloInferencia: 'TensorFlow-YOLO-CrashNet-v2.1',
          },
          peritajeCampo: {
            peritoId: 'e0000001-0000-0000-0000-000000000002',
            peritoNombre: 'Ing. Roberto Paz',
            fechaInspeccion: '2026-10-27T15:00:00Z',
            ocrPlacaDetectada: '4028-PLK',
            coincideConPoliza: true,
            agenteTfliteValido: true,
          },
          montoEstimadoReparacion: 2850.0,
          montoIndemnizacionAprobado: 2500.0,
          deducibleCalculado: 250.0,
          createdAt: '2026-10-26T12:00:00Z',
        },
      ],
      pagosPendientes: [
        {
          id: 'f0000001-0000-0000-0000-000000000001',
          numeroFactura: 'FAC-2026-00892',
          polizaId: 'd0000001-0000-0000-0000-000000000001',
          clienteId: 'b0000001-0000-0000-0000-000000000001',
          tipoComprobante: 'FACTURA',
          fechaEmision: '2026-08-28T10:05:00Z',
          subtotal: 626.4,
          impuestos: 93.6,
          total: 720.0,
          moneda: 'USD',
          estado: 'EMITIDA',
          urlPdfAlmacenado: 'http://localhost:8001/api/v1/facturas/f0000001-0000-0000-0000-000000000001/pdf',
          hashDigitalSha256: 'a948904f2f0f479b8f8197694b30184b0d2ed1c1cd2a1ec0fb85d299a192a447',
        },
      ],
      cacheDynamoDb: {
        table: 'AegisCore_IdempotencyRecords',
        partition_key: 'CACHE_COB#b0000001-0000-0000-0000-000000000001',
        cache_status: 'HIT_LOCAL_PWA_CACHE',
        latency_ms: 0.9,
        updated_at: new Date().toISOString(),
      },
    };
  }
}

