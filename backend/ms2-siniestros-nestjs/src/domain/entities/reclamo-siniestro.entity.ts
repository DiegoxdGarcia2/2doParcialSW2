import { UbicacionGeoVO } from '../value-objects/ubicacion-geo.vo';
import { SeveridadVO } from '../value-objects/severidad.vo';
import { EstadoReclamoVO, TipoEstadoReclamo } from '../value-objects/estado-reclamo.vo';
import { PeritajeDetalle } from './peritaje-detalle.entity';
import { TransicionEstadoInvalidaException } from '../exceptions/domain.exceptions';

export interface EntradaHistorialEstado {
  estado: TipoEstadoReclamo;
  fecha: Date;
  motivo?: string;
  autorId?: string;
}

export class ReclamoSiniestro {
  private _historialEstados: EntradaHistorialEstado[] = [];

  constructor(
    public readonly reclamoId: string,
    public readonly polizaId: string,
    public readonly clienteId: string,
    public readonly fechaSiniestro: Date,
    public readonly ubicacion: UbicacionGeoVO,
    public readonly descripcion: string,
    public severidad: SeveridadVO,
    private _estado: EstadoReclamoVO,
    public readonly fotosPreliminares: string[] = [],
    public peritoAsignadoId?: string,
    public peritaje?: PeritajeDetalle,
    historialInicial?: EntradaHistorialEstado[],
    public montoIndemnizacionAprobado?: number,
  ) {
    if (historialInicial && historialInicial.length > 0) {
      this._historialEstados = [...historialInicial];
    } else {
      this._historialEstados.push({
        estado: this._estado.valor,
        fecha: new Date(),
        motivo: 'Registro inicial del siniestro',
      });
    }
  }

  get estado(): EstadoReclamoVO {
    return this._estado;
  }

  get historialEstados(): ReadonlyArray<EntradaHistorialEstado> {
    return this._historialEstados;
  }

  /**
   * Asignar un perito ajustador al expediente (CU06 -> CU07)
   */
  asignarPerito(peritoId: string, autorId?: string): void {
    if (!this._estado.puedeAsignarPerito()) {
      throw new TransicionEstadoInvalidaException(
        this._estado.valor,
        'PERITAJE_ASIGNADO',
        'Solo se puede asignar perito a siniestros en estado REPORTADO_SOS o EN_TRIAJE.',
      );
    }
    this.peritoAsignadoId = peritoId;
    this.cambiarEstado('PERITAJE_ASIGNADO', `Perito asignado: ${peritoId}`, autorId);
  }

  /**
   * Registrar peritaje técnico sincronizado offline o en línea (CU07 / CU08)
   */
  registrarPeritaje(peritaje: PeritajeDetalle, autorId?: string): void {
    if (!this._estado.puedeRegistrarPeritaje()) {
      throw new TransicionEstadoInvalidaException(
        this._estado.valor,
        'PERITAJE_COMPLETADO',
        'El reclamo debe tener un perito asignado antes de completar la inspección.',
      );
    }
    this.peritaje = peritaje;
    this.cambiarEstado(
      'PERITAJE_COMPLETADO',
      `Peritaje completado con ${peritaje.partesDanadas.length} partes analizadas e IA. Monto estimado: BOB ${peritaje.montoEstimadoTotal}`,
      autorId || peritaje.peritoId,
    );
  }

  /**
   * Marcar el reclamo en proceso de liquidación (Paso 1 del Saga CU09)
   */
  marcarEnLiquidacion(motivo?: string): void {
    if (!this._estado.puedeIniciarLiquidacion()) {
      throw new TransicionEstadoInvalidaException(
        this._estado.valor,
        'EN_PROCESO_LIQUIDACION',
        'El reclamo debe contar con PERITAJE_COMPLETADO para ingresar a la orquestación Saga.',
      );
    }
    this.cambiarEstado(
      'EN_PROCESO_LIQUIDACION',
      motivo || 'Bloqueado por inicio de transacción Saga de liquidación transversal',
    );
  }

  /**
   * Reversión compensatoria de Saga en caso de fallo en pólizas o transferencias bancarias (CU09)
   */
  revertirEstado(motivo: string): void {
    if (!this._estado.puedeRevertirLiquidacion()) {
      throw new TransicionEstadoInvalidaException(
        this._estado.valor,
        'PERITAJE_COMPLETADO',
        'Solo se puede compensar un reclamo que se encuentra EN_PROCESO_LIQUIDACION.',
      );
    }
    this.cambiarEstado(
      'PERITAJE_COMPLETADO',
      `Compensación Saga ejecutada: ${motivo}`,
      'SAGA_ORCHESTRATOR',
    );
  }

  /**
   * Cierre exitoso tras confirmación del desembolso en Saga
   */
  finalizarLiquidacion(montoAprobado: number): void {
    if (this._estado.valor !== 'EN_PROCESO_LIQUIDACION') {
      throw new TransicionEstadoInvalidaException(
        this._estado.valor,
        'LIQUIDADO',
        'El reclamo debe estar en proceso de liquidación para finalizarse.',
      );
    }
    this.montoIndemnizacionAprobado = montoAprobado;
    this.cambiarEstado(
      'LIQUIDADO',
      `Liquidación exitosa completada por BOB ${montoAprobado}`,
      'MS3_ORCHESTRATOR',
    );
  }

  rechazar(motivo: string, autorId?: string): void {
    this.cambiarEstado('RECHAZADO', `Reclamo rechazado: ${motivo}`, autorId);
  }

  private cambiarEstado(
    nuevoEstado: TipoEstadoReclamo,
    motivo?: string,
    autorId?: string,
  ): void {
    this._estado = new EstadoReclamoVO(nuevoEstado);
    this._historialEstados.push({
      estado: nuevoEstado,
      fecha: new Date(),
      motivo,
      autorId,
    });
  }
}
