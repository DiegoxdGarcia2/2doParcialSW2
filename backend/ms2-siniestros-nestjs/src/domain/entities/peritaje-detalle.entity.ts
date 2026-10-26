export interface DanoParteVehiculo {
  parte: 'parachoques' | 'capo' | 'puertas' | 'faroles' | string;
  severidad: 'LEVE' | 'MODERADO' | 'GRAVE';
  costoEstimado: number;
  confianzaIa?: number; // Probabilidad devuelta por TensorFlow Lite (0.0 a 1.0)
}

export class PeritajeDetalle {
  constructor(
    public readonly peritoId: string,
    public readonly fechaInspeccion: Date,
    public readonly partesDanadas: DanoParteVehiculo[],
    public readonly montoEstimadoTotal: number,
    public readonly fotosEvidencia: string[],
    public readonly observaciones: string,
    public readonly sincronizadoOffline: boolean = false,
    public readonly hashIntegridadOffline?: string,
  ) {
    this.validar();
  }

  private validar(): void {
    if (!this.peritoId) {
      throw new Error('El ID del perito es obligatorio para registrar la inspección.');
    }
    if (this.montoEstimadoTotal < 0) {
      throw new Error('El monto estimado no puede ser negativo.');
    }
    if (!this.fotosEvidencia || this.fotosEvidencia.length === 0) {
      throw new Error('Se requiere al menos una fotografía de evidencia del peritaje.');
    }
  }

  tieneDanoEstructural(): boolean {
    return this.partesDanadas.some(
      (d) => d.severidad === 'GRAVE' || d.costoEstimado > 5000,
    );
  }
}
