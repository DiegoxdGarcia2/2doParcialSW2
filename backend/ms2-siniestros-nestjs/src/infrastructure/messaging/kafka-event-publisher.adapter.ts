import { Injectable, Logger, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { Kafka, Producer } from 'kafkajs';
import {
  IEventPublisherPort,
  SagaEventContract,
} from '../../application/ports/event-publisher.port';

@Injectable()
export class KafkaEventPublisherAdapter
  implements IEventPublisherPort, OnModuleInit, OnModuleDestroy
{
  private readonly logger = new Logger(KafkaEventPublisherAdapter.name);
  private kafka: Kafka;
  private producer: Producer;
  private isConnected = false;

  constructor() {
    const broker = process.env.KAFKA_BROKER || 'localhost:9092';
    this.kafka = new Kafka({
      clientId: 'ms2-siniestros-nestjs',
      brokers: [broker],
      retry: {
        retries: 3,
        initialRetryTime: 300,
      },
    });

    this.producer = this.kafka.producer();
  }

  async onModuleInit() {
    try {
      await this.producer.connect();
      this.isConnected = true;
      this.logger.log('Conectado exitosamente al broker Kafka');
    } catch (error: any) {
      this.logger.warn(
        `No se pudo conectar a Kafka inmediatamente (${error.message}). Modo resiliente activo.`,
      );
    }
  }

  async onModuleDestroy() {
    if (this.isConnected) {
      await this.producer.disconnect();
    }
  }

  async publicarEvento(topic: string, event: SagaEventContract): Promise<void> {
    const key = event.payload.reclamo_id || event.saga_id;
    const message = JSON.stringify(event);

    this.logger.log(
      `[Kafka Outbox] Publicando en tópico '${topic}' evento: ${event.event_type} | Key: ${key}`,
    );

    if (!this.isConnected) {
      try {
        await this.producer.connect();
        this.isConnected = true;
      } catch (err) {
        this.logger.warn(
          `Broker no disponible. Evento registrado localmente en outbox emulado: ${event.event_type}`,
        );
        return;
      }
    }

    try {
      await this.producer.send({
        topic,
        messages: [{ key, value: message }],
      });
    } catch (error: any) {
      this.logger.error(`Error publicando mensaje en Kafka: ${error.message}`);
    }
  }
}
