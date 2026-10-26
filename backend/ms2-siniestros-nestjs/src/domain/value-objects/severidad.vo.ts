export type NivelSeveridad = 'LEVE' | 'MODERADO' | 'GRAVE';

export class SeveridadVO {
  constructor(public readonly nivel: NivelSeveridad) {}

  /**
   * Triaje automático preliminar basado en la severidad reportada en el SOS móvil (CU06)
   */
  static calcularTriaje(params: {
    heridos: number;
    vehiculoInmovilizado: boolean;
    airbagDesplegado: boolean;
  }): SeveridadVO {
    if (params.heridos > 0 || params.airbagDesplegado) {
      return new SeveridadVO('GRAVE');
    }
    if (params.vehiculoInmovilizado) {
      return new SeveridadVO('MODERADO');
    }
    return new SeveridadVO('LEVE');
  }

  esGrave(): boolean {
    return this.nivel === 'GRAVE';
  }

  toString(): string {
    return this.nivel;
  }
}
