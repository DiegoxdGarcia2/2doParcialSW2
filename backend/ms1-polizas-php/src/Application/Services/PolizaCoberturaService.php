<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Application\Services;

use AegisCore\Polizas\Domain\Poliza\Repositories\PolizaRepositoryInterface;
use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;

/**
 * Objeto CONTROL de ICONIX (CU09 Paso 2 y Compensación: PolizaCoberturaService / PolizaCoverageService).
 * Participa en la Transacción Transversal Saga en 3 Microservicios (MS2 -> MS1 -> MS3):
 *   - Paso 2: descontarTechoAnualPoliza()
 *   - Rollback: compensarCoberturaSaga() / restituirSaldoCobertura()
 */
class PolizaCoberturaService
{
    public function __construct(
        private readonly PolizaRepositoryInterface $polizaRepository
    ) {
    }

    /**
     * Método operacional UML 2.5+ (CU09 Paso 2):
     * Verifica la vigencia de la póliza y descuenta el monto indemnizado del techo anual de cobertura.
     */
    public function descontarTechoAnualPoliza(
        string $polizaId,
        float $montoIndemnizacion,
        string $sagaId = 'saga-local',
        string $correlationId = 'corr-local',
        string $reclamoId = 'REC-2026-00492'
    ): array {
        $poliza = $this->polizaRepository->obtenerPorId($polizaId)
            ?? $this->polizaRepository->obtenerPorNumero($polizaId);

        if ($poliza === null) {
            throw new DomainException(
                sprintf('Póliza %s no encontrada para descuento de cobertura en Saga.', $polizaId),
                'POLICY_NOT_FOUND_SAGA',
                404
            );
        }

        $evento = $poliza->descontarTechoAnualPoliza($montoIndemnizacion, $sagaId, $correlationId, $reclamoId);
        $this->polizaRepository->guardar($poliza);

        return $evento->toPayload();
    }

    /**
     * Método operacional UML 2.5+ (CU09 Rollback / Plan Maestro pág. 8):
     * Ejecuta la transacción compensatoria devolviendo el monto descontado al saldo de la póliza.
     */
    public function compensarCoberturaSaga(
        string $polizaId,
        float $montoRestituir,
        string $sagaId = 'saga-local',
        string $correlationId = 'corr-local',
        string $reclamoId = 'REC-2026-00492',
        string $motivoFallo = 'Compensación automática por fallo en Paso 3 Spring Boot'
    ): array {
        $poliza = $this->polizaRepository->obtenerPorId($polizaId)
            ?? $this->polizaRepository->obtenerPorNumero($polizaId);

        if ($poliza === null) {
            throw new DomainException(
                sprintf('Póliza %s no encontrada para compensación de cobertura en Saga.', $polizaId),
                'POLICY_NOT_FOUND_SAGA',
                404
            );
        }

        $evento = $poliza->compensarCoberturaSaga(
            $montoRestituir,
            $sagaId,
            $correlationId,
            $reclamoId,
            $motivoFallo
        );
        $this->polizaRepository->guardar($poliza);

        return $evento->toPayload();
    }

    public function restituirSaldoCobertura(
        string $polizaId,
        float $montoRestituir,
        string $sagaId = 'saga-local',
        string $correlationId = 'corr-local',
        string $reclamoId = 'REC-2026-00492',
        string $motivoFallo = 'Rollback Saga MS3'
    ): array {
        return $this->compensarCoberturaSaga($polizaId, $montoRestituir, $sagaId, $correlationId, $reclamoId, $motivoFallo);
    }
}

