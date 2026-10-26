import { CommandHandler, ICommandHandler } from '@nestjs/cqrs';
import { Inject, Logger } from '@nestjs/common';
import { MarcarEnLiquidacionCommand } from './marcar-en-liquidacion.command';
import {
  IReclamoRepository,
  RECLAMO_REPOSITORY_TOKEN,
} from '../../../../domain/repositories/reclamo.repository.interface';
import {
  IEventPublisherPort,
  EVENT_PUBLISHER_PORT_TOKEN,
} from '../../../ports/event-publisher.port';

@CommandHandler(MarcarEnLiquidacionCommand)
export class MarcarEnLiquidacionHandler
  implements ICommandHandler<MarcarEnLiquidacionCommand, boolean>
{
  private readonly logger = new Logger(MarcarEnLiquidacionHandler.name);

  constructor(
    @Inject(RECLAMO_REPOSITORY_TOKEN)
    private readonly reclamoRepository: IReclamoRepository,
    @Inject(EVENT_PUBLISHER_PORT_TOKEN)
    private readonly eventPublisherPort: IEventPublisherPort,
  ) {}

  async execute(command: MarcarEnLiquidacionCommand): Promise<boolean> {
    this.logger.log(
      `[Saga CU09] Procesando MarcarReclamoEnLiquidacionCommand para Reclamo: ${command.reclamoId}, Saga: ${command.sagaId}`,
    );

    const reclamo = await this.reclamoRepository.findById(command.reclamoId);

    if (!reclamo) {
      this.logger.error(`Reclamo ${command.reclamoId} no encontrado para Saga ${command.sagaId}`);
      await this.eventPublisherPort.publicarEvento('aegiscore.saga.compensations', {
        saga_id: command.sagaId,
        correlation_id: command.correlationId,
        event_type: 'ReclamoBloqueoFallidoEvent',
        timestamp: new Date().toISOString(),
        source_service: 'ms2-siniestros-nestjs',
        payload: {
          reclamo_id: command.reclamoId,
          poliza_id: command.polizaId,
          motivo_fallo: `Reclamo con ID '${command.reclamoId}' no existe en la base de datos de siniestros.`,
          paso_fallido: 'PASO_1_NESTJS',
        },
      });
      return false;
    }

    try {
      reclamo.marcarEnLiquidacion(`Saga de liquidación iniciada: ${command.sagaId}`);
      await this.reclamoRepository.update(reclamo);

      this.logger.log(`Reclamo ${command.reclamoId} bloqueado con éxito. Emitiendo ReclamoMarcadoEnLiquidacionEvent`);

      await this.eventPublisherPort.publicarEvento('aegiscore.saga.events', {
        saga_id: command.sagaId,
        correlation_id: command.correlationId,
        event_type: 'ReclamoMarcadoEnLiquidacionEvent',
        timestamp: new Date().toISOString(),
        source_service: 'ms2-siniestros-nestjs',
        payload: {
          reclamo_id: reclamo.reclamoId,
          poliza_id: reclamo.polizaId,
          cliente_id: reclamo.clienteId,
          monto_indemnizacion: command.montoIndemnizacion || reclamo.peritaje?.montoEstimadoTotal || 0,
        },
      });

      return true;
    } catch (error: any) {
      this.logger.error(`Error transicionando estado del reclamo en Saga: ${error.message}`);

      await this.eventPublisherPort.publicarEvento('aegiscore.saga.compensations', {
        saga_id: command.sagaId,
        correlation_id: command.correlationId,
        event_type: 'ReclamoBloqueoFallidoEvent',
        timestamp: new Date().toISOString(),
        source_service: 'ms2-siniestros-nestjs',
        payload: {
          reclamo_id: command.reclamoId,
          poliza_id: command.polizaId,
          motivo_fallo: error.message,
          paso_fallido: 'PASO_1_NESTJS',
        },
      });

      return false;
    }
  }
}
