import { IQuery, IQueryHandler, QueryHandler } from '@nestjs/cqrs';
import { Inject } from '@nestjs/common';
import {
  IReclamoRepository,
  RECLAMO_REPOSITORY_TOKEN,
} from '../../../domain/repositories/reclamo.repository.interface';
import { ReclamoNotFoundException } from '../../../domain/exceptions/domain.exceptions';

export class ObtenerSiniestroPorIdQuery implements IQuery {
  constructor(public readonly reclamoId: string) {}
}

@QueryHandler(ObtenerSiniestroPorIdQuery)
export class ObtenerSiniestroPorIdHandler
  implements IQueryHandler<ObtenerSiniestroPorIdQuery, any>
{
  constructor(
    @Inject(RECLAMO_REPOSITORY_TOKEN)
    private readonly reclamoRepository: IReclamoRepository,
  ) {}

  async execute(query: ObtenerSiniestroPorIdQuery): Promise<any> {
    const reclamo = await this.reclamoRepository.findById(query.reclamoId);
    if (!reclamo) {
      throw new ReclamoNotFoundException(query.reclamoId);
    }

    return {
      reclamoId: reclamo.reclamoId,
      polizaId: reclamo.polizaId,
      clienteId: reclamo.clienteId,
      fechaSiniestro: reclamo.fechaSiniestro.toISOString(),
      ubicacion: {
        latitud: reclamo.ubicacion.latitud,
        longitud: reclamo.ubicacion.longitud,
        direccion: reclamo.ubicacion.direccion,
        geoJSON: reclamo.ubicacion.toGeoJSON(),
      },
      descripcion: reclamo.descripcion,
      severidad: reclamo.severidad.nivel,
      estado: reclamo.estado.valor,
      peritoAsignadoId: reclamo.peritoAsignadoId,
      montoIndemnizacionAprobado: reclamo.montoIndemnizacionAprobado,
      peritaje: reclamo.peritaje
        ? {
            peritoId: reclamo.peritaje.peritoId,
            fechaInspeccion: reclamo.peritaje.fechaInspeccion.toISOString(),
            partesDanadas: reclamo.peritaje.partesDanadas,
            montoEstimadoTotal: reclamo.peritaje.montoEstimadoTotal,
            fotosEvidencia: reclamo.peritaje.fotosEvidencia,
            observaciones: reclamo.peritaje.observaciones,
            sincronizadoOffline: reclamo.peritaje.sincronizadoOffline,
          }
        : null,
      historialEstados: reclamo.historialEstados,
    };
  }
}
