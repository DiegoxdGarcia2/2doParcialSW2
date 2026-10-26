import { Injectable, Logger } from '@nestjs/common';
import {
  INotificationPort,
  PushNotificationPayload,
} from '../../application/ports/notification.port';

@Injectable()
export class FcmNotificationAdapter implements INotificationPort {
  private readonly logger = new Logger(FcmNotificationAdapter.name);

  async enviarNotificacionPush(payload: PushNotificationPayload): Promise<boolean> {
    this.logger.log(
      `[Push FCM] Enviando notificación a topic/token: ${
        payload.topic || payload.tokenDestinatario || 'ALL_DEVICES'
      } | Título: "${payload.titulo}" | Mensaje: "${payload.mensaje}"`,
    );

    // Integración simulada con Firebase Cloud Messaging Admin SDK
    return true;
  }

  async notificarAsignacionPerito(
    peritoId: string,
    reclamoId: string,
    direccion?: string,
  ): Promise<boolean> {
    return this.enviarNotificacionPush({
      topic: `peritos_${peritoId}`,
      titulo: '🚨 Nueva Asignación de Inspección de Siniestro',
      mensaje: `Tienes asignado el reclamo ${reclamoId}. Ubicación: ${
        direccion || 'Ubicación en mapa'
      }.`,
      datosAdicionales: {
        tipo: 'ASIGNACION_PERITAJE',
        reclamoId,
      },
    });
  }

  async notificarEstadoSiniestro(
    clienteId: string,
    reclamoId: string,
    nuevoEstado: string,
  ): Promise<boolean> {
    return this.enviarNotificacionPush({
      topic: `clientes_${clienteId}`,
      titulo: 'Actualización de tu Siniestro - AegisCore AI',
      mensaje: `Expediente ${reclamoId}: ${nuevoEstado}`,
      datosAdicionales: {
        tipo: 'ESTADO_SINIESTRO',
        reclamoId,
      },
    });
  }
}
