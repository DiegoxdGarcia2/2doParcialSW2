import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { DynamoIdempotencyRepository } from './infrastructure/idempotency/dynamo-idempotency.repository';

import { HealthController } from './presentation/rest/controllers/health.controller';

@Module({
  imports: [
    MongooseModule.forRoot(
      process.env.MONGODB_URI || 'mongodb://localhost:27017/aegiscore_siniestros_db',
      {
      connectionFactory: (connection) => {
        connection.on('connected', () => {
          console.log('[MS2 NestJS] Conectado exitosamente a MongoDB Atlas Cloud');
        });
        connection.on('error', (err: any) => {
          console.error('[MS2 NestJS] Error en conexión MongoDB Atlas:', err);
        });
        return connection;
      },
    }),
  ],
  controllers: [HealthController],
  providers: [DynamoIdempotencyRepository],
  exports: [DynamoIdempotencyRepository],
})
export class AppModule {}
