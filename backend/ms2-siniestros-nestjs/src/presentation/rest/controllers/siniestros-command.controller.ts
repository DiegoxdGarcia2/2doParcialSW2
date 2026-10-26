import {
  Controller,
  Post,
  Body,
  Param,
  UseGuards,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { CommandBus } from '@nestjs/cqrs';
import { IdempotencyGuard } from '../../../infrastructure/idempotency/idempotency.guard';
import { RegistrarSiniestroDto } from '../dto/registrar-siniestro.dto';
import { SincronizarPeritajeDto } from '../dto/sincronizar-peritaje.dto';
import { RegistrarSiniestroCommand } from '../../../application/use-cases/commands/registrar-siniestro/registrar-siniestro.command';
import { SincronizarPeritajeCommand } from '../../../application/use-cases/commands/sincronizar-peritaje/sincronizar-peritaje.command';
import { AsignarPeritoCommand } from '../../../application/use-cases/commands/asignar-perito/asignar-perito.command';
import { MarcarEnLiquidacionCommand } from '../../../application/use-cases/commands/marcar-en-liquidacion/marcar-en-liquidacion.command';
import { RevertirEstadoReclamoCommand } from '../../../application/use-cases/commands/revertir-estado-reclamo/revertir-estado-reclamo.command';

@Controller('api/v1/siniestros')
export class SiniestrosCommandController {
  constructor(private readonly commandBus: CommandBus) {}

  /**
   * CU06: Registro de emergencia SOS móvil directo con triaje automático
   * Blindado contra reintentos por red inestable con Idempotency-Key
   */
  @Post('sos')
  @UseGuards(IdempotencyGuard)
  @HttpCode(HttpStatus.CREATED)
  async reportarSiniestroSos(@Body() dto: RegistrarSiniestroDto) {
    return this.commandBus.execute(
      new RegistrarSiniestroCommand(
        dto.polizaId,
        dto.clienteId,
        dto.latitud,
        dto.longitud,
        dto.descripcion,
        dto.direccion,
        dto.heridos,
        dto.vehiculoInmovilizado,
        dto.airbagDesplegado,
        dto.fotosPreliminares,
      ),
    );
  }

  /**
   * CU07 & CU08: Sincronización idempotente de peritaje móvil con Edge AI
   * Garantiza que inspecciones capturadas sin señal no se dupliquen al reconectar
   */
  @Post('peritaje/sync')
  @UseGuards(IdempotencyGuard)
  @HttpCode(HttpStatus.OK)
  async sincronizarPeritaje(@Body() dto: SincronizarPeritajeDto) {
    return this.commandBus.execute(
      new SincronizarPeritajeCommand(
        dto.reclamoId,
        dto.peritoId,
        dto.partesDanadas,
        dto.montoEstimadoTotal,
        dto.fotosEvidencia,
        dto.observaciones || '',
        dto.sincronizadoOffline,
        dto.hashIntegridadOffline,
      ),
    );
  }

  /**
   * Asignar perito ajustador al siniestro
   */
  @Post(':id/asignar-perito')
  @HttpCode(HttpStatus.OK)
  async asignarPerito(
    @Param('id') reclamoId: string,
    @Body('peritoId') peritoId: string,
    @Body('autorId') autorId?: string,
  ) {
    const success = await this.commandBus.execute(
      new AsignarPeritoCommand(reclamoId, peritoId, autorId),
    );
    return { reclamoId, peritoId, asignado: success };
  }

  /**
   * Endpoint de integración HTTP para Saga CU09 (alternativa directa a Kafka)
   */
  @Post('saga/marcar-en-liquidacion')
  @HttpCode(HttpStatus.OK)
  async marcarEnLiquidacionSaga(@Body() body: any) {
    const success = await this.commandBus.execute(
      new MarcarEnLiquidacionCommand(
        body.saga_id || 'manual-saga-id',
        body.correlation_id || body.reclamo_id,
        body.reclamo_id,
        body.poliza_id,
        body.monto_indemnizacion,
      ),
    );
    return { reclamo_id: body.reclamo_id, bloqueado: success };
  }

  /**
   * Endpoint de rollback compensatorio para Saga CU09
   */
  @Post('saga/revertir-estado')
  @HttpCode(HttpStatus.OK)
  async revertirEstadoSaga(@Body() body: any) {
    const success = await this.commandBus.execute(
      new RevertirEstadoReclamoCommand(
        body.saga_id || 'manual-saga-id',
        body.correlation_id || body.reclamo_id,
        body.reclamo_id,
        body.poliza_id,
        body.motivo_fallo || 'Compensación manual solicitada',
      ),
    );
    return { reclamo_id: body.reclamo_id, compensado: success };
  }
}
