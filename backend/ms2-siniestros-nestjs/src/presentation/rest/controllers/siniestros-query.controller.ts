import { Controller, Get, Param, Query } from '@nestjs/common';
import { QueryBus } from '@nestjs/cqrs';
import { ObtenerSiniestroPorIdQuery } from '../../../application/use-cases/queries/obtener-siniestro.query';
import { ListarPorClienteQuery } from '../../../application/use-cases/queries/listar-por-cliente.query';
import { ListarSiniestrosCercanosGeoQuery } from '../../../application/use-cases/queries/listar-cercanos-geo.query';

@Controller('api/v1/siniestros')
export class SiniestrosQueryController {
  constructor(private readonly queryBus: QueryBus) {}

  /**
   * Obtener expediente completo por ID
   */
  @Get(':id')
  async obtenerPorId(@Param('id') reclamoId: string) {
    return this.queryBus.execute(new ObtenerSiniestroPorIdQuery(reclamoId));
  }

  /**
   * Listar todos los siniestros de un asegurado
   */
  @Get('cliente/:clienteId')
  async listarPorCliente(@Param('clienteId') clienteId: string) {
    return this.queryBus.execute(new ListarPorClienteQuery(clienteId));
  }

  /**
   * Búsqueda geoespacial por radio en km (MongoDB 2dsphere)
   */
  @Get('geo/cercanos')
  async listarCercanos(
    @Query('lat') lat: string,
    @Query('lng') lng: string,
    @Query('radioKm') radioKm?: string,
  ) {
    const latNum = parseFloat(lat);
    const lngNum = parseFloat(lng);
    const radioNum = radioKm ? parseFloat(radioKm) : 10;
    return this.queryBus.execute(
      new ListarSiniestrosCercanosGeoQuery(latNum, lngNum, radioNum),
    );
  }
}
