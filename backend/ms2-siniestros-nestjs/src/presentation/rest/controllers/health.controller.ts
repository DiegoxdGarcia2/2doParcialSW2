import { Controller, Get } from '@nestjs/common';
import { InjectConnection } from '@nestjs/mongoose';
import { Connection } from 'mongoose';
import { DynamoIdempotencyRepository } from '../../../../infrastructure/idempotency/dynamo-idempotency.repository';

@Controller('health')
export class HealthController {
  constructor(
    @InjectConnection() private readonly mongoConnection: Connection,
    private readonly dynamoRepo: DynamoIdempotencyRepository,
  ) {}

  @Get()
  getHealth() {
    return {
      status: 'UP',
      service: 'ms2-siniestros-nestjs',
      architecture: 'Clean Architecture + CQRS',
      cloud_persistence: {
        document: 'MongoDB Atlas Cloud (aegiscore_siniestros_db)',
        idempotency: 'Amazon DynamoDB Cloud (AegisCore_IdempotencyRecords)',
      },
      timestamp: new Date().toISOString(),
    };
  }

  @Get('cloud-dbs')
  async getCloudDbsHealth() {
    const mongoState = this.mongoConnection.readyState;
    // 0 = disconnected, 1 = connected, 2 = connecting, 3 = disconnecting
    const mongoOk = mongoState === 1;

    let dynamoOk = false;
    let dynamoDetail: any = null;
    try {
      // Test querying a non-existent or dummy key to verify DynamoDB connectivity
      const testRecord = await this.dynamoRepo.findByKey('health-check-probe');
      dynamoOk = true;
      dynamoDetail = { status: 'CONNECTED', probe_result: testRecord ? 'FOUND' : 'NOT_FOUND' };
    } catch (err: any) {
      dynamoDetail = { status: 'ERROR', message: err.message };
    }

    return {
      status: mongoOk && dynamoOk ? 'ALL_HEALTHY' : 'DEGRADED',
      databases: {
        mongodb_atlas: {
          status: mongoOk ? 'CONNECTED' : 'DISCONNECTED',
          readyState: mongoState,
        },
        dynamodb_cloud: dynamoDetail,
      },
      timestamp: new Date().toISOString(),
    };
  }
}
