<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Poliza\Events;

use AegisCore\Polizas\Domain\Shared\Events\DomainEvent;

/**
 * Evento de Dominio: PolizaEmitidaEvent (CU04 / CU05).
 */
final class PolizaEmitidaEvent extends DomainEvent
{
    public function __construct(
        private readonly string $polizaId,
        private readonly string $numeroPoliza,
        private readonly string $clienteId,
        private readonly float $primaAnual,
        private readonly string $canalVenta
    ) {
        parent::__construct();
    }

    public function getEventName(): string
    {
        return 'PolizaEmitidaEvent';
    }

    public function toPayload(): array
    {
        return [
            'poliza_id' => $this->polizaId,
            'numero_poliza' => $this->numeroPoliza,
            'cliente_id' => $this->clienteId,
            'prima_anual' => $this->primaAnual,
            'canal_venta' => $this->canalVenta,
            'occurred_on' => $this->getOccurredOn()->format(DATE_ATOM),
        ];
    }
}

