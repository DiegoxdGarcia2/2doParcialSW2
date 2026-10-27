import { Injectable, Logger } from '@nestjs/common';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import {
  DynamoDBDocumentClient,
  GetCommand,
  PutCommand,
  UpdateCommand,
} from '@aws-sdk/lib-dynamodb';

export interface IdempotencyRecord {
  idempotencyKey: string;
  idempotency_key?: string;
  payload_hash: string;
  status: 'PROCESSING' | 'COMPLETED' | 'FAILED';
  http_status_code?: number;
  response_body_cached?: string;
  client_id?: string;
  created_at: string;
  expiresAt: number; // TTL attribute in DynamoDB
}

@Injectable()
export class DynamoIdempotencyRepository {
  private readonly logger = new Logger(DynamoIdempotencyRepository.name);
  private readonly docClient: DynamoDBDocumentClient;
  private readonly tableName: string;

  constructor() {
    this.tableName =
      process.env.DYNAMODB_TABLE_IDEMPOTENCY || 'AegisCore_IdempotencyRecords';

    const region = process.env.AWS_REGION || 'us-east-1';
    const accessKeyId = process.env.AWS_ACCESS_KEY_ID || 'local';
    const secretAccessKey = process.env.AWS_SECRET_ACCESS_KEY || 'local';
    const endpoint = process.env.DYNAMODB_ENDPOINT || 'http://127.0.0.1:8000';

    const clientConfig: any = {
      region,
      endpoint,
      credentials: {
        accessKeyId,
        secretAccessKey,
      },
    };

    const client = new DynamoDBClient(clientConfig);

    this.docClient = DynamoDBDocumentClient.from(client, {
      marshallOptions: {
        removeUndefinedValues: true,
      },
    });

    this.logger.log(
      `DynamoIdempotencyRepository inicializado para tabla: ${this.tableName} en region: ${region}`,
    );
  }

  /**
   * Busca un registro de idempotencia por clave (UUIDv4)
   */
  async findByKey(idempotencyKey: string): Promise<IdempotencyRecord | null> {
    try {
      const command = new GetCommand({
        TableName: this.tableName,
        Key: {
          idempotencyKey: idempotencyKey,
        },
      });

      const response = await this.docClient.send(command);
      return (response.Item as IdempotencyRecord) || null;
    } catch (error) {
      this.logger.error(`Error buscando clave de idempotencia ${idempotencyKey}:`, error);
      throw error;
    }
  }

  /**
   * Guarda un nuevo registro con estado 'PROCESSING' para adquirir el lock
   */
  async saveProcessingLock(
    idempotencyKey: string,
    payloadHash: string,
    clientId?: string,
    ttlSeconds = 86400,
  ): Promise<boolean> {
    const now = new Date();
    const expiresAt = Math.floor(now.getTime() / 1000) + ttlSeconds;

    const item: IdempotencyRecord = {
      idempotencyKey: idempotencyKey,
      idempotency_key: idempotencyKey,
      payload_hash: payloadHash,
      status: 'PROCESSING',
      client_id: clientId || 'UNKNOWN_CLIENT',
      created_at: now.toISOString(),
      expiresAt,
    };

    try {
      const command = new PutCommand({
        TableName: this.tableName,
        Item: item,
        ConditionExpression: 'attribute_not_exists(idempotencyKey)',
      });

      await this.docClient.send(command);
      return true;
    } catch (error: any) {
      if (error.name === 'ConditionalCheckFailedException') {
        // La clave ya existe
        return false;
      }
      this.logger.error(`Error adquiriendo lock de idempotencia:`, error);
      throw error;
    }
  }

  /**
   * Actualiza el registro a 'COMPLETED' guardando la respuesta en cache para replay instantaneo
   */
  async markCompleted(
    idempotencyKey: string,
    statusCode: number,
    responseBody: any,
  ): Promise<void> {
    try {
      const command = new UpdateCommand({
        TableName: this.tableName,
        Key: { idempotencyKey: idempotencyKey },
        UpdateExpression:
          'SET #status = :s, #code = :c, #resp = :r',
        ExpressionAttributeNames: {
          '#status': 'status',
          '#code': 'http_status_code',
          '#resp': 'response_body_cached',
        },
        ExpressionAttributeValues: {
          ':s': 'COMPLETED',
          ':c': statusCode,
          ':r': JSON.stringify(responseBody),
        },
      });

      await this.docClient.send(command);
    } catch (error) {
      this.logger.error(`Error completando registro de idempotencia ${idempotencyKey}:`, error);
      throw error;
    }
  }
}
