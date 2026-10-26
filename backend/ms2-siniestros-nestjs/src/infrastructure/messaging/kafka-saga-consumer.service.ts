import { Injectable, Logger, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { CommandBus } from '@nestjs/cqrs';
import { Kafka, Consumer } from 'kafkajs';
import { MarcarEnLiquidacionCommand } from '../../application/use-cases/commands/marcar-en-liquidacion/marcar-en-liquidacion.command';
import { RevertirEstadoReclamoCommand } from '../../application/use-cases/commands/revertir-estado-reclamo/revertir-estado-reclamo.command';

@Injectable()
export class KafkaSagaConsumerService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(KafkaSagaConsumerService.name);
  private kafka: Kafka;
  private consumer: Consumer;
  private isConnected = false;

  constructor(private readonly commandBus: CommandBus) {
    const broker = process.env.KAFKA_BROKER || 'localhost:9092';
    this.kafka = new Kafka({
      clientId: 'ms2-siniestros-saga-consumer',
      brokers: [broker],
    });

    this.consumer = this.kafka.consumer({
      groupId: 'ms2-siniestros-saga-group',
    });
  }

  async onModuleInit() {
    try {
      await this.consumer.connect();
      await this.consumer.subscribe({
        topics: ['aegiscore.saga.commands', 'aegiscore.saga.compensations'],
        fromBeginning: false,
      });

      this.isConnected = true;
      this.logger.log('Kafka Saga Consumer suscrito a tópicos de comandos y compensaciones');

      await this.consumer.run({
        eachMessage: async ({ topic, message }) => {
          if (!message.value) return;
          try {
            const raw = JSON.parse(message.value.toString());
            await this.procesarEvento(topic, raw);
          } catch (err: any) {
            this.logger.error(`Error parseando mensaje en tópico ${topic}: ${err.message}`);
          }
        },
      });
    } catch (error: any) {
      this.logger.warn(`Kafka Consumer no pudo conectar (${error.message}). Modo desacoplado activo.`);
    }
  }

  async onModuleDestroy() {
    if (this.isConnected) {
      await this.consumer.disconnect();
    }
  }

  private async procesarEvento(topic: string, event: any): Promise<void> {
    const { saga_id, correlation_id, event_type, payload } = event;

    if (event_type === 'MarcarReclamoEnLiquidacionCommand') {
      this.logger.log(`[Kafka Inbound] MarcarReclamoEnLiquidacionCommand para Reclamo ${payload.reclamo_id}`);
      await this.commandBus.execute(
        new MarcarEnLiquidacionCommand(
          saga_id,
          correlation_id,
          payload.reclamo_id,
          payload.poliza_id,
          payload.monto_indemnizacion,
        ),
      );
    } else if (event_type === 'RevertirEstadoReclamoCommand') {
      this.logger.warn(`[Kafka Inbound] RevertirEstadoReclamoCommand para Reclamo ${payload.reclamo_id}`);
      await this.commandBus.execute(
        new RevertirEstadoReclamoCommand(
          saga_id,
          correlation_id,
          payload.reclamo_id,
          payload.poliza_id,
          payload.motivo_fallo || 'Compensación Saga solicitada',
        ),
      );
    }
  }
}
