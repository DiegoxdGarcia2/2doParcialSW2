import { IQuery, IQueryHandler, QueryHandler } from '@nestjs/cqrs';
import { Inject } from '@nestjs/common';
import {
  IReclamoRepository,
  RECLAMO_REPOSITORY_TOKEN,
} from '../../../domain/repositories/reclamo.repository.interface';

export class ListarPorClienteQuery implements IQuery {
  constructor(public readonly clienteId: string) {}
}

@QueryHandler(ListarPorClienteQuery)
export class ListarPorClienteHandler implements IQueryHandler<ListarPorClienteQuery, any[]> {
  constructor(
    @Inject(RECLAMO_REPOSITORY_TOKEN)
    private readonly reclamoRepository: IReclamoRepository,
  ) {}

  async execute(query: ListarPorClienteQuery): Promise<any[]> {
    const reclamos = await this.reclamoRepository.findByClienteId(query.clienteId);
    return reclamos.map((r) => ({
      reclamoId: r.reclamoId,
      polizaId: r.polizaId,
      estado: r.estado.valor,
      severidad: r.severidad.nivel,
      descripcion: r.descripcion,
      fechaSiniestro: r.fechaSiniestro.toISOString(),
      montoEstimado: r.peritaje?.montoEstimadoTotal || 0,
    }));
  }
}
