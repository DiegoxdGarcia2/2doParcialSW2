import { ICommand } from '@nestjs/cqrs';

export class MarcarEnLiquidacionCommand implements ICommand {
  constructor(
    public readonly sagaId: string,
    public readonly correlationId: string,
    public readonly reclamoId: string,
    public readonly polizaId: string,
    public readonly montoIndemnizacion?: number,
  ) {}
}
