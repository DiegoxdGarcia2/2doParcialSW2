<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Poliza\Events;

use AegisCore\Polizas\Domain\Shared\Events\DomainEvent;

/**
 * Evento de Dominio Saga Compensación (CU09 Rollback): CoberturaRestituidaEvent.
 * Cumple exactamente con contracts/saga-events.schema.json.
 */
final class CoberturaRestituidaEvent extends DomainEvent
{
    public function __construct(
        private readonly string $sagaId,
        private readonly string $correlationId,
        private readonly string $reclamoId,
        private readonly string $polizaId,
        private readonly float $montoRestituido,
        private readonly float $saldoCoberturaPrevio,
        private readonly float $saldoCoberturaRestante,
        private readonly string $motivoFallo
    ) {
        parent::__construct();
    }

    public function getEventName(): string
    {
        return 'CoberturaRestituidaEvent';
    }

    public function toPayload(): array
    {
        return [
            'saga_id' => $this->sagaId,
            'correlation_id' => $this->correlationId,
            'event_type' => $this->getEventName(),
            'timestamp' => $this->getOccurredOn()->format(DATE_ATOM),
            'source_service' => 'ms1-polizas-php',
            'target_topic' => 'aegiscore.saga.compensations',
            'payload' => [
                'reclamo_id' => $this->reclamoId,
                'poliza_id' => $this->polizaId,
                'monto_indemnizacion' => $this->montoRestituido,
                'saldo_cobertura_previo' => $this->saldoCoberturaPrevio,
                'saldo_cobertura_restante' => $this->saldoCoberturaRestante,
                'motivo_fallo' => $this->motivoFallo,
            ],
        ];
    }
}

