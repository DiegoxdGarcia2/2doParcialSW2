import { ICommand } from '@nestjs/cqrs';

export class RegistrarSiniestroCommand implements ICommand {
  constructor(
    public readonly polizaId: string,
    public readonly clienteId: string,
    public readonly latitud: number,
    public readonly longitud: number,
    public readonly descripcion: string,
    public readonly direccion?: string,
    public readonly heridos: number = 0,
    public readonly vehiculoInmovilizado: boolean = false,
    public readonly airbagDesplegado: boolean = false,
    public readonly fotosPreliminares: string[] = [],
  ) {}
}
