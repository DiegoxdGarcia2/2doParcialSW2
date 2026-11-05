<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Poliza\Events;

use AegisCore\Polizas\Domain\Shared\Events\DomainEvent;

/**
 * Evento de Dominio Saga (CU09 Paso 2): CoberturaPolizaDescontadaEvent.
 * Cumple exactamente con contracts/saga-events.schema.json.
 */
final class CoberturaPolizaDescontadaEvent extends DomainEvent
{
    public function __construct(
        private readonly string $sagaId,
        private readonly string $correlationId,
        private readonly string $reclamoId,
        private readonly string $polizaId,
        private readonly float $montoIndemnizacion,
        private readonly float $saldoCoberturaPrevio,
        private readonly float $saldoCoberturaRestante
    ) {
        parent::__construct();
    }

    public function getEventName(): string
    {
        return 'CoberturaPolizaDescontadaEvent';
    }

    public function toPayload(): array
    {
        return [
            'saga_id' => $this->sagaId,
            'correlation_id' => $this->correlationId,
            'event_type' => $this->getEventName(),
            'timestamp' => $this->getOccurredOn()->format(DATE_ATOM),
            'source_service' => 'ms1-polizas-php',
            'target_topic' => 'aegiscore.saga.events',
            'payload' => [
                'reclamo_id' => $this->reclamoId,
                'poliza_id' => $this->polizaId,
                'monto_indemnizacion' => $this->montoIndemnizacion,
                'saldo_cobertura_previo' => $this->saldoCoberturaPrevio,
                'saldo_cobertura_restante' => $this->saldoCoberturaRestante,
            ],
        ];
    }
}

