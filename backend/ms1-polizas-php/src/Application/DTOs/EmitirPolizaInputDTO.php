<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Application\DTOs;

/**
 * DTO de entrada para Emitir Póliza (CU04 / CU05 - EmitirPolizaInput en supergraph.graphql).
 */
final class EmitirPolizaInputDTO
{
    public function __construct(
        public readonly string $clienteId,
        public readonly string $planId,
        public readonly array $datosBien,
        public readonly string $fechaInicio,
        public readonly int $mesesVigencia = 12,
        public readonly string $canalVenta = 'WEB_REACT',
        public readonly ?string $tokenValidacionNitidezLocal = null,
        public readonly ?string $documento = null,
        public readonly ?string $placa = null
    ) {
    }

    public static function fromArray(array $input): self
    {
        $placaDirecta = isset($input['placa']) ? (string)$input['placa'] : null;
        $datosBien = (array)($input['datosBien'] ?? []);
        if ($placaDirecta !== null && !isset($datosBien['placa'])) {
            $datosBien['placa'] = $placaDirecta;
        }

        return new self(
            (string)($input['clienteId'] ?? 'b0000001-0000-0000-0000-000000000001'),
            (string)($input['planId'] ?? 'a0000001-0000-0000-0000-000000000001'),
            $datosBien,
            (string)($input['fechaInicio'] ?? gmdate('Y-m-d\TH:i:s\Z')),
            (int)($input['mesesVigencia'] ?? 12),
            (string)($input['canalVenta'] ?? 'WEB_REACT'),
            isset($input['tokenValidacionNitidezLocal']) ? (string)$input['tokenValidacionNitidezLocal'] : null,
            isset($input['documento']) ? (string)$input['documento'] : null,
            $placaDirecta
        );
    }
}

