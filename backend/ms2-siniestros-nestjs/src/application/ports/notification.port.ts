export const NOTIFICATION_PORT_TOKEN = 'INotificationPort';

export interface PushNotificationPayload {
  tokenDestinatario?: string;
  topic?: string;
  titulo: string;
  mensaje: string;
  datosAdicionales?: Record<string, string>;
}

export interface INotificationPort {
  enviarNotificacionPush(payload: PushNotificationPayload): Promise<boolean>;
  notificarAsignacionPerito(peritoId: string, reclamoId: string, direccion?: string): Promise<boolean>;
  notificarEstadoSiniestro(clienteId: string, reclamoId: string, nuevoEstado: string): Promise<boolean>;
}
