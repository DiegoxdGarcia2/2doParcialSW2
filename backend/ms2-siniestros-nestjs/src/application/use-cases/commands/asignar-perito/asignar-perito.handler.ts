import { CommandHandler, ICommandHandler } from '@nestjs/cqrs';
import { Inject, Logger } from '@nestjs/common';
import { AsignarPeritoCommand } from './asignar-perito.command';
import {
  IReclamoRepository,
  RECLAMO_REPOSITORY_TOKEN,
} from '../../../../domain/repositories/reclamo.repository.interface';
import {
  INotificationPort,
  NOTIFICATION_PORT_TOKEN,
} from '../../../ports/notification.port';
import { ReclamoNotFoundException } from '../../../../domain/exceptions/domain.exceptions';

@CommandHandler(AsignarPeritoCommand)
export class AsignarPeritoHandler implements ICommandHandler<AsignarPeritoCommand, boolean> {
  private readonly logger = new Logger(AsignarPeritoHandler.name);

  constructor(
    @Inject(RECLAMO_REPOSITORY_TOKEN)
    private readonly reclamoRepository: IReclamoRepository,
    @Inject(NOTIFICATION_PORT_TOKEN)
    private readonly notificationPort: INotificationPort,
  ) {}

  async execute(command: AsignarPeritoCommand): Promise<boolean> {
    const reclamo = await this.reclamoRepository.findById(command.reclamoId);
    if (!reclamo) {
      throw new ReclamoNotFoundException(command.reclamoId);
    }

    reclamo.asignarPerito(command.peritoId, command.autorId);
    await this.reclamoRepository.update(reclamo);

    this.logger.log(`Perito ${command.peritoId} asignado al reclamo ${command.reclamoId}`);

    // Notificar al perito vía push FCM
    await this.notificationPort.notificarAsignacionPerito(
      command.peritoId,
      reclamo.reclamoId,
      reclamo.ubicacion.direccion,
    );

    return true;
  }
}
