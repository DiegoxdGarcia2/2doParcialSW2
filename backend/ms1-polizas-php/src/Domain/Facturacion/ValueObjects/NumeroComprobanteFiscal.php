<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Facturacion\ValueObjects;

use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;

/**
 * Value Object DDD: NumeroComprobanteFiscal (FACTURA / NOTA_VENTA).
 */
final class NumeroComprobanteFiscal
{
    private string $numeroFactura;
    private string $tipoComprobante;

    public function __construct(string $numeroFactura, string $tipoComprobante = 'FACTURA')
    {
        $tipo = strtoupper(trim($tipoComprobante));
        if (!in_array($tipo, ['FACTURA', 'NOTA_VENTA'], true)) {
            throw new DomainException("Tipo de comprobante fiscal inválido: {$tipoComprobante}", 'INVALID_INVOICE_TYPE');
        }
        $num = strtoupper(trim($numeroFactura));
        if ($num === '') {
            throw new DomainException('El número de factura no puede estar vacío.', 'EMPTY_INVOICE_NUMBER');
        }
        $this->numeroFactura = $num;
        $this->tipoComprobante = $tipo;
    }

    public static function generarNuevo(string $tipoComprobante = 'FACTURA'): self
    {
        $prefijo = strtoupper($tipoComprobante) === 'NOTA_VENTA' ? 'NV' : 'FAC';
        $codigo = sprintf('%s-%s-%05d', $prefijo, date('Y'), random_int(1000, 99999));
        return new self($codigo, $tipoComprobante);
    }

    public function numeroFactura(): string
    {
        return $this->numeroFactura;
    }

    public function tipoComprobante(): string
    {
        return $this->tipoComprobante;
    }
}

