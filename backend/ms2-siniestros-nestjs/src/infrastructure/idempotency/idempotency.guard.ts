import {
  Injectable,
  CanActivate,
  ExecutionContext,
  BadRequestException,
  ConflictException,
  UnprocessableEntityException,
  Logger,
} from '@nestjs/common';
import * as crypto from 'crypto';
import { DynamoIdempotencyRepository } from './dynamo-idempotency.repository';

const UUIDV4_REGEX =
  /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

@Injectable()
export class IdempotencyGuard implements CanActivate {
  private readonly logger = new Logger(IdempotencyGuard.name);

  constructor(private readonly idempotencyRepo: DynamoIdempotencyRepository) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const http = context.switchToHttp();
    const req = http.getRequest();
    const res = http.getResponse();

    const rawKey = req.headers['idempotency-key'] || req.headers['Idempotency-Key'] || req.headers['x-idempotency-key'] || req.headers['X-Idempotency-Key'];

    // Si la petición no incluye clave de idempotencia, se permite continuar o se exige si es POST/PUT
    if (!rawKey) {
      if (req.method === 'POST' || req.method === 'PUT') {
        throw new BadRequestException(
          'El encabezado Idempotency-Key (UUIDv4) es obligatorio para garantizar tolerancia a reintentos (Contrato CU08/CU10).',
        );
      }
      return true;
    }

    const idempotencyKey = String(rawKey).trim();

    if (!UUIDV4_REGEX.test(idempotencyKey)) {
      throw new BadRequestException(
        `El encabezado Idempotency-Key '${idempotencyKey}' no tiene un formato UUIDv4 válido.`,
      );
    }

    // Calcular hash SHA-256 del cuerpo HTTP de la petición
    const bodyStr = JSON.stringify(req.body || {});
    const payloadHash = crypto.createHash('sha256').update(bodyStr).digest('hex');
    const clientId = String(req.headers['x-client-id'] || 'FLUTTER_MOBILE');

    // Consultar registro en DynamoDB
    const existing = await this.idempotencyRepo.findByKey(idempotencyKey);

    if (existing) {
      if (existing.status === 'COMPLETED') {
        // Verificar integridad del payload
        if (existing.payload_hash !== payloadHash) {
          this.logger.warn(`Idempotency payload mismatch para clave ${idempotencyKey}`);
          throw new UnprocessableEntityException({
            error: 'IDEMPOTENCY_PAYLOAD_MISMATCH',
            message:
              'El cuerpo de la petición no coincide con el payload original registrado para este Idempotency-Key.',
          });
        }

        // Replay instantáneo (<5ms)
        this.logger.log(`Cache HIT Idempotencia DynamoDB para clave: ${idempotencyKey}`);
        res.setHeader('X-Cache-Lookup', 'HIT_IDEMPOTENCY_DYNAMODB');
        const statusCode = existing.http_status_code || 200;
        const body = existing.response_body_cached
          ? JSON.parse(existing.response_body_cached)
          : { status: 'COMPLETED' };

        res.status(statusCode).json(body);
        return false; // Detener flujo posterior porque ya se respondió
      }

      if (existing.status === 'PROCESSING') {
        this.logger.warn(`Petición concurrente en proceso para clave: ${idempotencyKey}`);
        throw new ConflictException({
          error: 'CONCURRENT_REQUEST_IN_PROGRESS',
          message:
            'Una transacción con esta clave de idempotencia ya se encuentra en procesamiento.',
        });
      }
    }

    // Adquirir lock en DynamoDB
    const lockAdquirido = await this.idempotencyRepo.saveProcessingLock(
      idempotencyKey,
      payloadHash,
      clientId,
    );

    if (!lockAdquirido) {
      throw new ConflictException({
        error: 'CONCURRENT_REQUEST_IN_PROGRESS',
        message: 'No se pudo adquirir el bloqueo de idempotencia para la transacción concurrente.',
      });
    }

    // Interceptar la respuesta para persistir COMPLETED al terminar
    const originalJson = res.json.bind(res);
    const repo = this.idempotencyRepo;

    res.json = (bodyData: any) => {
      const statusCode = res.statusCode || 200;
      if (statusCode >= 200 && statusCode < 300) {
        repo
          .markCompleted(idempotencyKey, statusCode, bodyData)
          .catch((err) =>
            this.logger.error(`Error guardando estado COMPLETED en DynamoDB:`, err),
          );
      }
      return originalJson(bodyData);
    };

    return true;
  }
}
