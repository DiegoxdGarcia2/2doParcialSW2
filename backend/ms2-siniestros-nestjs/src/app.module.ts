import { Module } from '@nestjs/common';
import { CqrsModule } from '@nestjs/cqrs';
import { MongooseModule } from '@nestjs/mongoose';

// MongoDB Schemas
import {
  ReclamoMongoEntity,
  ReclamoMongoSchema,
} from './infrastructure/persistence/mongo/schemas/reclamo.schema';

// Repositories & Adapters
import { RECLAMO_REPOSITORY_TOKEN } from './domain/repositories/reclamo.repository.interface';
import { MongoReclamoRepository } from './infrastructure/persistence/mongo/repositories/mongo-reclamo.repository';
import { DynamoIdempotencyRepository } from './infrastructure/idempotency/dynamo-idempotency.repository';
import { IdempotencyGuard } from './infrastructure/idempotency/idempotency.guard';

// Ports & Adapters
import { NOTIFICATION_PORT_TOKEN } from './application/ports/notification.port';
import { FcmNotificationAdapter } from './infrastructure/notifications/fcm-notification.adapter';
import { EVENT_PUBLISHER_PORT_TOKEN } from './application/ports/event-publisher.port';
import { KafkaEventPublisherAdapter } from './infrastructure/messaging/kafka-event-publisher.adapter';
import { KafkaSagaConsumerService } from './infrastructure/messaging/kafka-saga-consumer.service';

// Command Handlers
import { RegistrarSiniestroHandler } from './application/use-cases/commands/registrar-siniestro/registrar-siniestro.handler';
import { SincronizarPeritajeHandler } from './application/use-cases/commands/sincronizar-peritaje/sincronizar-peritaje.handler';
import { AsignarPeritoHandler } from './application/use-cases/commands/asignar-perito/asignar-perito.handler';
import { MarcarEnLiquidacionHandler } from './application/use-cases/commands/marcar-en-liquidacion/marcar-en-liquidacion.handler';
import { RevertirEstadoReclamoHandler } from './application/use-cases/commands/revertir-estado-reclamo/revertir-estado-reclamo.handler';

// Query Handlers
import { ObtenerSiniestroPorIdHandler } from './application/use-cases/queries/obtener-siniestro.query';
import { ListarPorClienteHandler } from './application/use-cases/queries/listar-por-cliente.query';
import { ListarSiniestrosCercanosGeoHandler } from './application/use-cases/queries/listar-cercanos-geo.query';

// Controllers
import { HealthController } from './presentation/rest/controllers/health.controller';
import { SiniestrosCommandController } from './presentation/rest/controllers/siniestros-command.controller';
import { SiniestrosQueryController } from './presentation/rest/controllers/siniestros-query.controller';

const CommandHandlers = [
  RegistrarSiniestroHandler,
  SincronizarPeritajeHandler,
  AsignarPeritoHandler,
  MarcarEnLiquidacionHandler,
  RevertirEstadoReclamoHandler,
];

const QueryHandlers = [
  ObtenerSiniestroPorIdHandler,
  ListarPorClienteHandler,
  ListarSiniestrosCercanosGeoHandler,
];

@Module({
  imports: [
    CqrsModule,
    MongooseModule.forRoot(
      process.env.MONGODB_URI || 'mongodb://localhost:27017/aegiscore_siniestros_db',
      {
        connectionFactory: (connection) => {
          connection.on('connected', () => {
            console.log('[MS2 NestJS] Conectado exitosamente a MongoDB');
          });
          connection.on('error', (err: any) => {
            console.error('[MS2 NestJS] Advertencia de conexión MongoDB:', err.message || err);
          });
          return connection;
        },
      },
    ),
    MongooseModule.forFeature([
      { name: ReclamoMongoEntity.name, schema: ReclamoMongoSchema },
    ]),
  ],
  controllers: [
    HealthController,
    SiniestrosCommandController,
    SiniestrosQueryController,
  ],
  providers: [
    {
      provide: RECLAMO_REPOSITORY_TOKEN,
      useClass: MongoReclamoRepository,
    },
    {
      provide: NOTIFICATION_PORT_TOKEN,
      useClass: FcmNotificationAdapter,
    },
    {
      provide: EVENT_PUBLISHER_PORT_TOKEN,
      useClass: KafkaEventPublisherAdapter,
    },
    DynamoIdempotencyRepository,
    IdempotencyGuard,
    KafkaSagaConsumerService,
    ...CommandHandlers,
    ...QueryHandlers,
  ],
  exports: [
    RECLAMO_REPOSITORY_TOKEN,
    DynamoIdempotencyRepository,
    IdempotencyGuard,
  ],
})
export class AppModule {}
