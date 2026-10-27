import { CommandHandler, ICommandHandler } from '@nestjs/cqrs';
import { Inject, Logger } from '@nestjs/common';
import { SincronizarPeritajeCommand } from './sincronizar-peritaje.command';
import {
  IReclamoRepository,
  RECLAMO_REPOSITORY_TOKEN,
} from '../../../../domain/repositories/reclamo.repository.interface';
import {
  INotificationPort,
  NOTIFICATION_PORT_TOKEN,
} from '../../../ports/notification.port';
import {
  IEventPublisherPort,
  EVENT_PUBLISHER_PORT_TOKEN,
} from '../../../ports/event-publisher.port';
import { ReclamoNotFoundException } from '../../../../domain/exceptions/domain.exceptions';
import { PeritajeDetalle } from '../../../../domain/entities/peritaje-detalle.entity';
import { ReclamoSiniestro } from '../../../../domain/entities/reclamo-siniestro.entity';
import { UbicacionGeoVO } from '../../../../domain/value-objects/ubicacion-geo.vo';
import { SeveridadVO, NivelSeveridad } from '../../../../domain/value-objects/severidad.vo';
import { EstadoReclamoVO } from '../../../../domain/value-objects/estado-reclamo.vo';

export interface PeritajeSincronizadoDTO {
  reclamoId: string;
  peritoId: string;
  estado: string;
  montoEstimadoTotal: number;
  partesEvaluadasCount: number;
  sincronizadoOffline: boolean;
  mensaje: string;
}

@CommandHandler(SincronizarPeritajeCommand)
export class SincronizarPeritajeHandler
  implements ICommandHandler<SincronizarPeritajeCommand, PeritajeSincronizadoDTO>
{
  private readonly logger = new Logger(SincronizarPeritajeHandler.name);

  constructor(
    @Inject(RECLAMO_REPOSITORY_TOKEN)
    private readonly reclamoRepository: IReclamoRepository,
    @Inject(NOTIFICATION_PORT_TOKEN)
    private readonly notificationPort: INotificationPort,
    @Inject(EVENT_PUBLISHER_PORT_TOKEN)
    private readonly eventPublisherPort: IEventPublisherPort,
  ) {}

  async execute(command: SincronizarPeritajeCommand): Promise<PeritajeSincronizadoDTO> {
    this.logger.log(`Sincronizando peritaje técnico para reclamo: ${command.reclamoId}`);

    let reclamo = await this.reclamoRepository.findById(command.reclamoId);
    if (!reclamo) {
      this.logger.log(
        `Reclamo ${command.reclamoId} no existía previamente en base de datos. Creando expediente desde peritaje offline...`,
      );
      reclamo = new ReclamoSiniestro(
        command.reclamoId,
        'POL-AUTO-' + command.reclamoId,
        'CLI-PERITAJE-MOVIL',
        new Date(),
        new UbicacionGeoVO(-17.7833, -63.1812, 'Inspección Móvil Peritaje'),
        command.observaciones || 'Siniestro levantado directamente en campo offline',
        new SeveridadVO('MODERADO'),
        new EstadoReclamoVO('PERITAJE_ASIGNADO'),
        command.fotosEvidencia,
        command.peritoId,
      );
      await this.reclamoRepository.save(reclamo);
    }

    // 1. Instanciar entidad PeritajeDetalle (ejecuta invariantes y validación)
    const peritaje = new PeritajeDetalle(
      command.peritoId,
      new Date(),
      command.partesDanadas,
      command.montoEstimadoTotal,
      command.fotosEvidencia,
      command.observaciones,
      command.sincronizadoOffline,
      command.hashIntegridadOffline,
    );

    // 2. Si aún no tenía perito asignado formalmente, se asocia
    if (!reclamo.peritoAsignadoId) {
      reclamo.asignarPerito(command.peritoId, 'SISTEMA_AUTO_SYNC');
    }

    // 3. Registrar en el Aggregate Root (transiciona a PERITAJE_COMPLETADO)
    reclamo.registrarPeritaje(peritaje, command.peritoId);

    // 4. Actualizar en MongoDB Atlas
    await this.reclamoRepository.update(reclamo);
    this.logger.log(
      `Peritaje registrado exitosamente en MongoDB. Reclamo ${reclamo.reclamoId} listo para liquidación`,
    );

    // 5. Notificar por Push al cliente
    await this.notificationPort.notificarEstadoSiniestro(
      reclamo.clienteId,
      reclamo.reclamoId,
      `Inspección técnica completada. Monto valorado: BOB ${command.montoEstimadoTotal.toFixed(2)}`,
    );

    // 6. Publicar evento opcional a Kafka para alertar que el expediente está listo
    await this.eventPublisherPort.publicarEvento('aegiscore.saga.events', {
      saga_id: '00000000-0000-0000-0000-000000000000',
      correlation_id: reclamo.reclamoId,
      event_type: 'PeritajeCompletadoEvent',
      timestamp: new Date().toISOString(),
      source_service: 'ms2-siniestros-nestjs',
      payload: {
        reclamo_id: reclamo.reclamoId,
        poliza_id: reclamo.polizaId,
        cliente_id: reclamo.clienteId,
        monto_indemnizacion: command.montoEstimadoTotal,
      },
    });

    return {
      reclamoId: reclamo.reclamoId,
      peritoId: command.peritoId,
      estado: reclamo.estado.valor,
      montoEstimadoTotal: command.montoEstimadoTotal,
      partesEvaluadasCount: command.partesDanadas.length,
      sincronizadoOffline: command.sincronizadoOffline,
      mensaje: 'Peritaje técnico sincronizado exitosamente con evaluación de daños y Edge AI',
    };
  }
}
