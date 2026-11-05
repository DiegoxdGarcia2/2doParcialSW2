<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Shared\ValueObjects;

use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;
use DateTimeImmutable;

/**
 * Value Object DDD (Requerido explícitamente en CU03/CU04): VigenciaPoliza.
 * Garantiza que fechaFin >= fechaInicio y permite verificar cobertura activa en cualquier fecha.
 */
final class VigenciaPoliza
{
    private DateTimeImmutable $fechaInicio;
    private DateTimeImmutable $fechaFin;

    public function __construct(string|DateTimeImmutable $fechaInicio, string|DateTimeImmutable $fechaFin)
    {
        $inicio = $fechaInicio instanceof DateTimeImmutable
            ? $fechaInicio
            : new DateTimeImmutable($fechaInicio);
        $fin = $fechaFin instanceof DateTimeImmutable
            ? $fechaFin
            : new DateTimeImmutable($fechaFin);

        if ($fin < $inicio) {
            throw new DomainException(
                sprintf(
                    'La fecha de fin de vigencia (%s) no puede ser anterior a la fecha de inicio (%s).',
                    $fin->format('Y-m-d'),
                    $inicio->format('Y-m-d')
                ),
                'INVALID_POLICY_VALIDITY_RANGE'
            );
        }

        $this->fechaInicio = $inicio;
        $this->fechaFin = $fin;
    }

    public static function desdeMeses(string|DateTimeImmutable $fechaInicio, int $mesesVigencia = 12): self
    {
        if ($mesesVigencia < 1 || $mesesVigencia > 60) {
            throw new DomainException(
                'Los meses de vigencia de una póliza deben estar entre 1 y 60 meses.',
                'INVALID_VALIDITY_MONTHS'
            );
        }
        $inicio = $fechaInicio instanceof DateTimeImmutable
            ? $fechaInicio
            : new DateTimeImmutable($fechaInicio);
        $fin = $inicio->modify(sprintf('+%d months', $mesesVigencia));
        return new self($inicio, $fin);
    }

    public function fechaInicio(): DateTimeImmutable
    {
        return $this->fechaInicio;
    }

    public function fechaFin(): DateTimeImmutable
    {
        return $this->fechaFin;
    }

    public function fechaInicioIso(): string
    {
        return $this->fechaInicio->format('Y-m-d\TH:i:s\Z');
    }

    public function fechaFinIso(): string
    {
        return $this->fechaFin->format('Y-m-d\TH:i:s\Z');
    }

    public function estaVigente(?DateTimeImmutable $fechaReferencia = null): bool
    {
        $ref = $fechaReferencia ?? new DateTimeImmutable('now');
        $refDate = $ref->format('Y-m-d');
        return $refDate >= $this->fechaInicio->format('Y-m-d')
            && $refDate <= $this->fechaFin->format('Y-m-d');
    }

    public function diasRestantes(?DateTimeImmutable $fechaReferencia = null): int
    {
        $ref = $fechaReferencia ?? new DateTimeImmutable('now');
        if ($ref > $this->fechaFin) {
            return 0;
        }
        return (int)$ref->diff($this->fechaFin)->days;
    }
}

