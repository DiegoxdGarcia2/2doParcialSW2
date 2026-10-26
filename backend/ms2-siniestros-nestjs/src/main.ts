import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { ValidationPipe, Logger } from '@nestjs/common';
import { AppModule } from './app.module';

async function bootstrap() {
  const logger = new Logger('MS2-Bootstrap');
  const app = await NestFactory.create(AppModule);

  app.enableCors({
    origin: '*',
    methods: 'GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS',
    credentials: true,
  });

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      transform: true,
      forbidNonWhitelisted: false,
    }),
  );

  const port = process.env.PORT || 8002;
  await app.listen(port);

  logger.log(`==================================================================`);
  logger.log(`🛡️  MS2 Siniestros NestJS 10 corriendo en puerto: ${port}`);
  logger.log(`🏛️  Patrón: Clean Architecture + CQRS + Idempotency DynamoDB`);
  logger.log(`🍃  Persistencia: MongoDB Atlas Cloud (2dsphere geospatial)`);
  logger.log(`⚡  Endpoints base: http://localhost:${port}/health y /api/v1/siniestros`);
  logger.log(`==================================================================`);
}

bootstrap();
