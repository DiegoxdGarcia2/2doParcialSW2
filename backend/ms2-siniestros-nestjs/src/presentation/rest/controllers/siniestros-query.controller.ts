import { Controller, Get, Param, Query, BadRequestException } from '@nestjs/common';
import { QueryBus } from '@nestjs/cqrs';
import { ObtenerSiniestroPorIdQuery } from '../../../application/use-cases/queries/obtener-siniestro.query';
import { ListarPorClienteQuery } from '../../../application/use-cases/queries/listar-por-cliente.query';
import { ListarSiniestrosCercanosGeoQuery } from '../../../application/use-cases/queries/listar-cercanos-geo.query';

@Controller('api/v1/siniestros')
export class SiniestrosQueryController {
  constructor(private readonly queryBus: QueryBus) {}

  /**
   * 1. Búsqueda geoespacial por radio en km (MongoDB 2dsphere) - DEBE IR PRIMERO
   */
  @Get('geo/cercanos')
  async listarCercanos(
    @Query('lat') lat: string,
    @Query('lng') lng: string,
    @Query('radioKm') radioKm?: string,
  ) {
    const latNum = parseFloat(lat);
    const lngNum = parseFloat(lng);
    if (isNaN(latNum) || isNaN(lngNum) || latNum < -90 || latNum > 90 || lngNum < -180 || lngNum > 180) {
      throw new BadRequestException('Parámetros lat (-90 a 90) y lng (-180 a 180) son obligatorios y numéricos.');
    }
    const radioNum = radioKm && !isNaN(parseFloat(radioKm)) ? parseFloat(radioKm) : 10;
    return this.queryBus.execute(
      new ListarSiniestrosCercanosGeoQuery(latNum, lngNum, radioNum),
    );
  }

  /**
   * 2. Listar todos los siniestros de un asegurado
   */
  @Get('cliente/:clienteId')
  async listarPorCliente(@Param('clienteId') clienteId: string) {
    return this.queryBus.execute(new ListarPorClienteQuery(clienteId));
  }

  /**
   * 3. Obtener expediente completo por ID - AL FINAL
   */
  @Get(':id')
  async obtenerPorId(@Param('id') reclamoId: string) {
    return this.queryBus.execute(new ObtenerSiniestroPorIdQuery(reclamoId));
  }
}
