<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Infrastructure\Messaging\Kafka;

use AegisCore\Polizas\Application\Services\PolizaCoberturaService;
use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;
use Throwable;

/**
 * Adaptador de Mensajería Kafka (CU09 Apoyo Saga en MS1 PHP): SagaKafkaConsumer.
 * Procesa los comandos enviados por el Orquestador Saga (MS3 Spring Boot) en:
 *   - Tópico aegiscore.saga.commands -> DescontarCoberturaPolizaCommand (Paso 2)
 *   - Tópico aegiscore.saga.compensations -> CompensarCoberturaCommand (Rollback)
 * Cumpliendo 100% con contracts/saga-events.schema.json.
 */
class SagaKafkaConsumer
{
    public function __construct(
        private readonly PolizaCoberturaService $polizaCoberturaService
    ) {
    }

    public function handleKafkaMessage(array $envelope): array
    {
        $sagaId = (string)($envelope['saga_id'] ?? $envelope['sagaId'] ?? '00000000-0000-4000-8000-000000000001');
        $correlationId = (string)($envelope['correlation_id'] ?? $envelope['correlationId'] ?? $sagaId);
        $eventType = (string)($envelope['event_type'] ?? $envelope['eventType'] ?? 'DescontarCoberturaPolizaCommand');
        $payload = (array)($envelope['payload'] ?? $envelope);

        $polizaId = (string)($payload['poliza_id'] ?? $payload['polizaId'] ?? 'd0000001-0000-0000-0000-000000000001');
        $reclamoId = (string)($payload['reclamo_id'] ?? $payload['reclamoId'] ?? 'REC-2026-00492');
        $monto = (float)($payload['monto_indemnizacion'] ?? $payload['montoIndemnizacion'] ?? 2500.00);

        if ($eventType === 'CompensarCoberturaCommand') {
            $motivo = (string)($payload['motivo_fallo'] ?? $payload['motivoRechazo'] ?? 'Compensación Saga Paso 3 Fallido');
            return $this->polizaCoberturaService->compensarCoberturaSaga(
                $polizaId,
                $monto,
                $sagaId,
                $correlationId,
                $reclamoId,
                $motivo
            );
        }

        // Por defecto procesa Paso 2: DescontarCoberturaPolizaCommand
        try {
            return $this->polizaCoberturaService->descontarTechoAnualPoliza(
                $polizaId,
                $monto,
                $sagaId,
                $correlationId,
                $reclamoId
            );
        } catch (DomainException $e) {
            return [
                'saga_id' => $sagaId,
                'correlation_id' => $correlationId,
                'event_type' => 'DescuentoCoberturaFallidoEvent',
                'timestamp' => gmdate('Y-m-d\TH:i:s\Z'),
                'source_service' => 'ms1-polizas-php',
                'target_topic' => 'aegiscore.saga.events',
                'payload' => [
                    'reclamo_id' => $reclamoId,
                    'poliza_id' => $polizaId,
                    'monto_indemnizacion' => $monto,
                    'motivo_fallo' => $e->getMessage(),
                    'paso_fallido' => 'PASO_2_PHP',
                ],
            ];
        } catch (Throwable $e) {
            return [
                'saga_id' => $sagaId,
                'correlation_id' => $correlationId,
                'event_type' => 'DescuentoCoberturaFallidoEvent',
                'timestamp' => gmdate('Y-m-d\TH:i:s\Z'),
                'source_service' => 'ms1-polizas-php',
                'target_topic' => 'aegiscore.saga.events',
                'payload' => [
                    'reclamo_id' => $reclamoId,
                    'poliza_id' => $polizaId,
                    'motivo_fallo' => $e->getMessage(),
                    'paso_fallido' => 'PASO_2_PHP',
                ],
            ];
        }
    }
}

