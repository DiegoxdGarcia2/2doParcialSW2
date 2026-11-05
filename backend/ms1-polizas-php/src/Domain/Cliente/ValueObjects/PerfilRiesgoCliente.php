<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Cliente\ValueObjects;

use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;

/**
 * Value Object DDD: PerfilRiesgoCliente (Score Crediticio 300-950 y Nivel de Riesgo).
 */
final class PerfilRiesgoCliente
{
    private const PERFILES_VALIDOS = ['BAJO', 'MODERADO', 'ALTO', 'CRITICO'];

    private int $scoreCrediticio;
    private string $perfilRiesgo;

    public function __construct(int $scoreCrediticio = 750, ?string $perfilRiesgo = null)
    {
        if ($scoreCrediticio < 300 || $scoreCrediticio > 950) {
            throw new DomainException(
                sprintf('El score crediticio debe estar entre 300 y 950 (recibido: %d).', $scoreCrediticio),
                'INVALID_CREDIT_SCORE'
            );
        }

        $this->scoreCrediticio = $scoreCrediticio;
        if ($perfilRiesgo !== null && in_array(strtoupper(trim($perfilRiesgo)), self::PERFILES_VALIDOS, true)) {
            $this->perfilRiesgo = strtoupper(trim($perfilRiesgo));
        } else {
            $this->perfilRiesgo = self::inferirPerfilPorScore($scoreCrediticio);
        }
    }

    public static function inferirPerfilPorScore(int $score): string
    {
        if ($score >= 780) {
            return 'BAJO';
        }
        if ($score >= 650) {
            return 'MODERADO';
        }
        if ($score >= 500) {
            return 'ALTO';
        }
        return 'CRITICO';
    }

    public function scoreCrediticio(): int
    {
        return $this->scoreCrediticio;
    }

    public function perfilRiesgo(): string
    {
        return $this->perfilRiesgo;
    }

    public function factorDescuentoComercial(): float
    {
        return match ($this->perfilRiesgo) {
            'BAJO' => 0.12,      // 12% de descuento para conductores prudentes
            'MODERADO' => 0.05,  // 5% de descuento
            'ALTO' => 0.00,
            'CRITICO' => -0.15,  // Recargo del 15%
            default => 0.00,
        };
    }
}

