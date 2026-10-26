export const EVENT_PUBLISHER_PORT_TOKEN = 'IEventPublisherPort';

export interface SagaEventContract {
  saga_id: string;
  correlation_id: string;
  event_type: string;
  timestamp: string;
  source_service: 'ms2-siniestros-nestjs';
  target_topic?: string;
  payload: {
    reclamo_id: string;
    poliza_id: string;
    cliente_id?: string;
    monto_indemnizacion?: number;
    motivo_fallo?: string;
    paso_fallido?: string;
    [key: string]: any;
  };
}

export interface IEventPublisherPort {
  publicarEvento(topic: string, event: SagaEventContract): Promise<void>;
}
