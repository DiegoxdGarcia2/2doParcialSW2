export type TipoEstadoReclamo =
  | 'REPORTADO_SOS'
  | 'EN_TRIAJE'
  | 'PERITAJE_ASIGNADO'
  | 'PERITAJE_COMPLETADO'
  | 'EN_PROCESO_LIQUIDACION'
  | 'LIQUIDADO'
  | 'RECHAZADO';

export class EstadoReclamoVO {
  constructor(public readonly valor: TipoEstadoReclamo) {}

  puedeAsignarPerito(): boolean {
    return this.valor === 'REPORTADO_SOS' || this.valor === 'EN_TRIAJE';
  }

  puedeRegistrarPeritaje(): boolean {
    return this.valor === 'PERITAJE_ASIGNADO' || this.valor === 'EN_TRIAJE';
  }

  puedeIniciarLiquidacion(): boolean {
    return this.valor === 'PERITAJE_COMPLETADO';
  }

  puedeRevertirLiquidacion(): boolean {
    return this.valor === 'EN_PROCESO_LIQUIDACION';
  }

  toString(): string {
    return this.valor;
  }
}
