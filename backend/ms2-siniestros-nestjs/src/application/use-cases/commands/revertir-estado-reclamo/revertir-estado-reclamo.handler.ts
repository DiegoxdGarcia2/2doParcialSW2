import { CommandHandler, ICommandHandler } from '@nestjs/cqrs';
import { Inject, Logger } from '@nestjs/common';
import { RevertirEstadoReclamoCommand } from './revertir-estado-reclamo.command';
import {
  IReclamoRepository,
  RECLAMO_REPOSITORY_TOKEN,
} from '../../../../domain/repositories/reclamo.repository.interface';
import {
  IEventPublisherPort,
  EVENT_PUBLISHER_PORT_TOKEN,
} from '../../../ports/event-publisher.port';

@CommandHandler(RevertirEstadoReclamoCommand)
export class RevertirEstadoReclamoHandler
  implements ICommandHandler<RevertirEstadoReclamoCommand, boolean>
{
  private readonly logger = new Logger(RevertirEstadoReclamoHandler.name);

  constructor(
    @Inject(RECLAMO_REPOSITORY_TOKEN)
    private readonly reclamoRepository: IReclamoRepository,
    @Inject(EVENT_PUBLISHER_PORT_TOKEN)
    private readonly eventPublisherPort: IEventPublisherPort,
  ) {}

  async execute(command: RevertirEstadoReclamoCommand): Promise<boolean> {
    this.logger.warn(
      `[Saga CU09 Compensación] RevertirEstadoReclamoCommand recibido para reclamo: ${command.reclamoId}. Motivo: ${command.motivoFallo}`,
    );

    const reclamo = await this.reclamoRepository.findById(command.reclamoId);
    if (!reclamo) {
      this.logger.error(`No se pudo compensar: Reclamo ${command.reclamoId} no existe.`);
      return false;
    }

    try {
      reclamo.revertirEstado(command.motivoFallo);
      await this.reclamoRepository.update(reclamo);

      this.logger.log(`Compensación exitosa: Reclamo ${command.reclamoId} revertido a PERITAJE_COMPLETADO`);

      await this.eventPublisherPort.publicarEvento('aegiscore.saga.events', {
        saga_id: command.sagaId,
        correlation_id: command.correlationId,
        event_type: 'EstadoReclamoRevertidoEvent',
        timestamp: new Date().toISOString(),
        source_service: 'ms2-siniestros-nestjs',
        payload: {
          reclamo_id: reclamo.reclamoId,
          poliza_id: reclamo.polizaId,
          motivo_fallo: command.motivoFallo,
        },
      });

      return true;
    } catch (error: any) {
      this.logger.error(`Fallo durante la compensación del reclamo ${command.reclamoId}: ${error.message}`);
      return false;
    }
  }
}
