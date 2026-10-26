import { CommandHandler, ICommandHandler } from '@nestjs/cqrs';
import { Inject, Logger } from '@nestjs/common';
import { RegistrarSiniestroCommand } from './registrar-siniestro.command';
import {
  IReclamoRepository,
  RECLAMO_REPOSITORY_TOKEN,
} from '../../../../domain/repositories/reclamo.repository.interface';
import {
  INotificationPort,
  NOTIFICATION_PORT_TOKEN,
} from '../../../ports/notification.port';
import { ReclamoSiniestro } from '../../../../domain/entities/reclamo-siniestro.entity';
import { UbicacionGeoVO } from '../../../../domain/value-objects/ubicacion-geo.vo';
import { SeveridadVO } from '../../../../domain/value-objects/severidad.vo';
import { EstadoReclamoVO } from '../../../../domain/value-objects/estado-reclamo.vo';

export interface SiniestroRegistradoDTO {
  reclamoId: string;
  polizaId: string;
  clienteId: string;
  severidad: string;
  estado: string;
  fechaSiniestro: string;
  mensaje: string;
}

@CommandHandler(RegistrarSiniestroCommand)
export class RegistrarSiniestroHandler
  implements ICommandHandler<RegistrarSiniestroCommand, SiniestroRegistradoDTO>
{
  private readonly logger = new Logger(RegistrarSiniestroHandler.name);

  constructor(
    @Inject(RECLAMO_REPOSITORY_TOKEN)
    private readonly reclamoRepository: IReclamoRepository,
    @Inject(NOTIFICATION_PORT_TOKEN)
    private readonly notificationPort: INotificationPort,
  ) {}

  async execute(command: RegistrarSiniestroCommand): Promise<SiniestroRegistradoDTO> {
    this.logger.log(`Procesando registro de siniestro SOS para póliza: ${command.polizaId}`);

    // 1. Obtener ID correlativo
    const reclamoId = await this.reclamoRepository.generarSiguienteReclamoId();

    // 2. Construir Value Objects
    const ubicacion = new UbicacionGeoVO(command.latitud, command.longitud, command.direccion);
    const severidad = SeveridadVO.calcularTriaje({
      heridos: command.heridos,
      vehiculoInmovilizado: command.vehiculoInmovilizado,
      airbagDesplegado: command.airbagDesplegado,
    });
    const estadoInicial = new EstadoReclamoVO('REPORTADO_SOS');

    // 3. Crear Aggregate Root
    const reclamo = new ReclamoSiniestro(
      reclamoId,
      command.polizaId,
      command.clienteId,
      new Date(),
      ubicacion,
      command.descripcion,
      severidad,
      estadoInicial,
      command.fotosPreliminares,
    );

    // 4. Persistir en MongoDB
    await this.reclamoRepository.save(reclamo);
    this.logger.log(`Siniestro ${reclamoId} persistido exitosamente en MongoDB`);

    // 5. Emitir notificación Push FCM
    await this.notificationPort.notificarEstadoSiniestro(
      command.clienteId,
      reclamoId,
      `Siniestro registrado con severidad ${severidad.nivel}. Un perito será asignado a la brevedad.`,
    );

    return {
      reclamoId: reclamo.reclamoId,
      polizaId: reclamo.polizaId,
      clienteId: reclamo.clienteId,
      severidad: reclamo.severidad.nivel,
      estado: reclamo.estado.valor,
      fechaSiniestro: reclamo.fechaSiniestro.toISOString(),
      mensaje: 'Reclamo de emergencia SOS recibido y triado con éxito',
    };
  }
}
