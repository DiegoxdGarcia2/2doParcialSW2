<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Catalogo\ValueObjects;

use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;

/**
 * Value Object DDD: TipoPlanVO (VEHICULAR, SALUD, VIDA, HOGAR).
 */
final class TipoPlanVO
{
    private const TIPOS_PERMITIDOS = ['VEHICULAR', 'SALUD', 'VIDA', 'HOGAR'];

    private string $valor;

    public function __construct(string $valor)
    {
        $normalizado = strtoupper(trim($valor));
        if (!in_array($normalizado, self::TIPOS_PERMITIDOS, true)) {
            throw new DomainException(
                sprintf('Tipo de plan inválido: %s. Permitidos: %s', $valor, implode(', ', self::TIPOS_PERMITIDOS)),
                'INVALID_PLAN_TYPE'
            );
        }
        $this->valor = $normalizado;
    }

    public function valor(): string
    {
        return $this->valor;
    }
}

