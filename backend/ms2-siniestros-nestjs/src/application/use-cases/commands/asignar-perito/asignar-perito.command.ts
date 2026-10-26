import { ICommand } from '@nestjs/cqrs';

export class AsignarPeritoCommand implements ICommand {
  constructor(
    public readonly reclamoId: string,
    public readonly peritoId: string,
    public readonly autorId?: string,
  ) {}
}
