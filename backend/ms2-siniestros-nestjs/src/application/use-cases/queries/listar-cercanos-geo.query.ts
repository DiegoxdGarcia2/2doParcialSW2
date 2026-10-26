import { IQuery, IQueryHandler, QueryHandler } from '@nestjs/cqrs';
import { Inject } from '@nestjs/common';
import {
  IReclamoRepository,
  RECLAMO_REPOSITORY_TOKEN,
} from '../../../domain/repositories/reclamo.repository.interface';

export class ListarSiniestrosCercanosGeoQuery implements IQuery {
  constructor(
    public readonly latitud: number,
    public readonly longitud: number,
    public readonly radioKm: number = 10,
  ) {}
}

@QueryHandler(ListarSiniestrosCercanosGeoQuery)
export class ListarSiniestrosCercanosGeoHandler
  implements IQueryHandler<ListarSiniestrosCercanosGeoQuery, any[]>
{
  constructor(
    @Inject(RECLAMO_REPOSITORY_TOKEN)
    private readonly reclamoRepository: IReclamoRepository,
  ) {}

  async execute(query: ListarSiniestrosCercanosGeoQuery): Promise<any[]> {
    const reclamos = await this.reclamoRepository.findCercanos(
      query.latitud,
      query.longitud,
      query.radioKm,
    );

    return reclamos.map((r) => ({
      reclamoId: r.reclamoId,
      polizaId: r.polizaId,
      clienteId: r.clienteId,
      estado: r.estado.valor,
      severidad: r.severidad.nivel,
      ubicacion: {
        latitud: r.ubicacion.latitud,
        longitud: r.ubicacion.longitud,
        direccion: r.ubicacion.direccion,
      },
      fechaSiniestro: r.fechaSiniestro.toISOString(),
    }));
  }
}
