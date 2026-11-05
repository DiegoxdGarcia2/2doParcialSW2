<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Shared\ValueObjects;

use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;

/**
 * Value Object DDD (Requerido explícitamente en CU03/CU04): PrimaMonetaria.
 * Encapsula montos financieros e invariantes de moneda (USD / BOB).
 */
final class PrimaMonetaria
{
    private float $monto;
    private string $moneda;

    public function __construct(float $monto, string $moneda = 'USD')
    {
        if ($monto < 0) {
            throw new DomainException(
                sprintf('El monto monetario no puede ser negativo (recibido: %.2f).', $monto),
                'NEGATIVE_MONETARY_AMOUNT'
            );
        }

        $monedaNormalizada = strtoupper(trim($moneda));
        if (!in_array($monedaNormalizada, ['USD', 'BOB'], true)) {
            throw new DomainException(
                sprintf('Moneda no soportada en el dominio asegurador: %s', $moneda),
                'UNSUPPORTED_CURRENCY'
            );
        }

        $this->monto = round($monto, 2);
        $this->moneda = $monedaNormalizada;
    }

    public function monto(): float
    {
        return $this->monto;
    }

    public function moneda(): string
    {
        return $this->moneda;
    }

    public function calcularPrimaMensual(): self
    {
        return new self(round($this->monto / 12.0, 2), $this->moneda);
    }

    public function sumar(self $otro): self
    {
        $this->verificarMismaMoneda($otro);
        return new self($this->monto + $otro->monto, $this->moneda);
    }

    public function descontar(self $otro): self
    {
        $this->verificarMismaMoneda($otro);
        if ($otro->monto > $this->monto) {
            throw new DomainException(
                sprintf(
                    'Saldo insuficiente para descontar %.2f %s del disponible %.2f %s.',
                    $otro->monto,
                    $this->moneda,
                    $this->monto,
                    $this->moneda
                ),
                'INSUFFICIENT_COVERAGE_BALANCE'
            );
        }
        return new self($this->monto - $otro->monto, $this->moneda);
    }

    public function aplicarFactor(float $factor): self
    {
        return new self(round($this->monto * $factor, 2), $this->moneda);
    }

    private function verificarMismaMoneda(self $otro): void
    {
        if ($this->moneda !== $otro->moneda) {
            throw new DomainException(
                sprintf('No se pueden operar monedas distintas (%s vs %s).', $this->moneda, $otro->moneda),
                'CURRENCY_MISMATCH'
            );
        }
    }

    public function toArray(): array
    {
        return [
            'monto' => $this->monto,
            'moneda' => $this->moneda,
        ];
    }
}

