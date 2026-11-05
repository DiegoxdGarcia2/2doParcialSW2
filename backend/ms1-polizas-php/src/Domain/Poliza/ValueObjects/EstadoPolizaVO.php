<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Poliza\ValueObjects;

use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;

/**
 * Value Object DDD: EstadoPolizaVO.
 */
final class EstadoPolizaVO
{
    public const COTIZADA = 'COTIZADA';
    public const EMITIDA = 'EMITIDA';
    public const ACTIVA = 'ACTIVA';
    public const SUSPENDIDA = 'SUSPENDIDA';
    public const VENCIDA = 'VENCIDA';
    public const CANCELADA = 'CANCELADA';

    private const ESTADOS_VALIDOS = [
        self::COTIZADA,
        self::EMITIDA,
        self::ACTIVA,
        self::SUSPENDIDA,
        self::VENCIDA,
        self::CANCELADA,
    ];

    private string $valor;

    public function __construct(string $valor)
    {
        $norm = strtoupper(trim($valor));
        if (!in_array($norm, self::ESTADOS_VALIDOS, true)) {
            throw new DomainException(
                sprintf('Estado de póliza no válido: %s', $valor),
                'INVALID_POLICY_STATE'
            );
        }
        $this->valor = $norm;
    }

    public function valor(): string
    {
        return $this->valor;
    }

    public function permiteDescuentoCobertura(): bool
    {
        return in_array($this->valor, [self::ACTIVA, self::EMITIDA], true);
    }
}

