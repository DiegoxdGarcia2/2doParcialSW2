import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import { IdempotencyGuard } from './idempotency.guard';
import {
  BadRequestException,
  ConflictException,
  UnprocessableEntityException,
  ExecutionContext,
} from '@nestjs/common';
import * as crypto from 'crypto';

describe('Infrastructure: IdempotencyGuard (CU08 / CU10 Protocol)', () => {
  let guard: IdempotencyGuard;
  let mockRepo: any;

  const validUuid = '9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d';
  const testPayload = { reclamoId: 'REC-001', monto: 1200 };
  const calculatedHash = crypto
    .createHash('sha256')
    .update(JSON.stringify(testPayload))
    .digest('hex');

  beforeEach(() => {
    mockRepo = {
      findByKey: jest.fn<any>().mockImplementation(() => Promise.resolve(null)),
      saveProcessingLock: jest.fn<any>().mockImplementation(() => Promise.resolve(true)),
      markCompleted: jest.fn<any>().mockImplementation(() => Promise.resolve()),
    };

    guard = new IdempotencyGuard(mockRepo);
  });

  function createMockContext(headers: any, body: any, method = 'POST') {
    const res: any = {
      setHeader: jest.fn(),
      status: jest.fn().mockReturnThis(),
      json: jest.fn().mockReturnThis(),
      statusCode: 200,
    };
    const req: any = {
      headers,
      body,
      method,
    };

    return {
      switchToHttp: () => ({
        getRequest: () => req,
        getResponse: () => res,
      }),
    } as unknown as ExecutionContext;
  }

  it('debe rechazar con 400 si falta el encabezado Idempotency-Key en método POST', async () => {
    const ctx = createMockContext({}, testPayload);
    await expect(guard.canActivate(ctx)).rejects.toThrow(BadRequestException);
  });

  it('debe rechazar con 400 si el Idempotency-Key no es un UUIDv4 válido', async () => {
    const ctx = createMockContext({ 'idempotency-key': 'clave-no-uuid' }, testPayload);
    await expect(guard.canActivate(ctx)).rejects.toThrow(BadRequestException);
  });

  it('debe responder con 200 en cache y cabecera X-Cache-Lookup si ya fue procesada (Replay)', async () => {
    mockRepo.findByKey.mockImplementation(() =>
      Promise.resolve({
        idempotencyKey: validUuid,
        payload_hash: calculatedHash,
        status: 'COMPLETED',
        http_status_code: 201,
        response_body_cached: JSON.stringify({ ok: true, id: 'REC-001' }),
        created_at: new Date().toISOString(),
        expiresAt: 1234567,
      }),
    );

    const ctx = createMockContext({ 'idempotency-key': validUuid }, testPayload);
    const res = ctx.switchToHttp().getResponse();

    const result = await guard.canActivate(ctx);

    expect(result).toBe(false); // Detiene flujo porque ya respondió con cache
    expect(res.setHeader).toHaveBeenCalledWith('X-Cache-Lookup', 'HIT_IDEMPOTENCY_DYNAMODB');
    expect(res.status).toHaveBeenCalledWith(201);
    expect(res.json).toHaveBeenCalledWith({ ok: true, id: 'REC-001' });
  });

  it('debe retornar 422 si el hash del cuerpo no coincide con el guardado en DynamoDB', async () => {
    mockRepo.findByKey.mockImplementation(() =>
      Promise.resolve({
        idempotencyKey: validUuid,
        payload_hash: 'otro-hash-distinto-que-no-coincide',
        status: 'COMPLETED',
        created_at: new Date().toISOString(),
        expiresAt: 1234567,
      }),
    );

    const ctx = createMockContext({ 'idempotency-key': validUuid }, testPayload);
    await expect(guard.canActivate(ctx)).rejects.toThrow(UnprocessableEntityException);
  });

  it('debe retornar 409 si la clave de idempotencia aún está en estado PROCESSING', async () => {
    mockRepo.findByKey.mockImplementation(() =>
      Promise.resolve({
        idempotencyKey: validUuid,
        payload_hash: calculatedHash,
        status: 'PROCESSING',
        created_at: new Date().toISOString(),
        expiresAt: 1234567,
      }),
    );

    const ctx = createMockContext({ 'idempotency-key': validUuid }, testPayload);
    await expect(guard.canActivate(ctx)).rejects.toThrow(ConflictException);
  });

  it('debe permitir continuar y adquirir lock si la clave es nueva', async () => {
    mockRepo.findByKey.mockImplementation(() => Promise.resolve(null));

    const ctx = createMockContext({ 'idempotency-key': validUuid }, testPayload);
    const result = await guard.canActivate(ctx);

    expect(result).toBe(true);
    expect(mockRepo.saveProcessingLock).toHaveBeenCalledWith(
      validUuid,
      calculatedHash,
      'FLUTTER_MOBILE',
    );
  });
});
