<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Application\DTOs;

/**
 * DTO de entrada para Cotizar Póliza en Línea (CU04 - CotizarPolizaInput en supergraph.graphql).
 */
final class CotizarPolizaInputDTO
{
    public function __construct(
        public readonly string $tipoPlan,
        public readonly string $planId,
        public readonly int $edadConductor,
        public readonly array $datosBien,
        public readonly string $ciudad = 'Santa Cruz'
    ) {
    }

    public static function fromArray(array $input): self
    {
        return new self(
            (string)($input['tipoPlan'] ?? 'VEHICULAR'),
            (string)($input['planId'] ?? 'a0000001-0000-0000-0000-000000000001'),
            (int)($input['edadConductor'] ?? 32),
            (array)($input['datosBien'] ?? []),
            (string)($input['ciudad'] ?? 'Santa Cruz')
        );
    }
}

