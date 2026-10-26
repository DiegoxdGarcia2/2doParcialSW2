import { ICommand } from '@nestjs/cqrs';
import { DanoParteVehiculo } from '../../../../domain/entities/peritaje-detalle.entity';

export class SincronizarPeritajeCommand implements ICommand {
  constructor(
    public readonly reclamoId: string,
    public readonly peritoId: string,
    public readonly partesDanadas: DanoParteVehiculo[],
    public readonly montoEstimadoTotal: number,
    public readonly fotosEvidencia: string[],
    public readonly observaciones: string,
    public readonly sincronizadoOffline: boolean = false,
    public readonly hashIntegridadOffline?: string,
  ) {}
}
