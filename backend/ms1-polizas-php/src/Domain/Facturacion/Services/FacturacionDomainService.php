<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Facturacion\Services;

use AegisCore\Polizas\Domain\Facturacion\Entities\FacturaNotaVenta;
use AegisCore\Polizas\Domain\Facturacion\ValueObjects\NumeroComprobanteFiscal;
use AegisCore\Polizas\Domain\Poliza\Entities\Poliza;
use AegisCore\Polizas\Domain\Shared\ValueObjects\UuidId;

/**
 * Servicio de Dominio DDD: FacturacionDomainService (CU05).
 * Construye el comprobante fiscal (Factura o Nota de Venta) desglosando IVA (13%) y subtotal neto.
 */
class FacturacionDomainService
{
    public function emitirComprobanteParaPoliza(Poliza $poliza, string $tipoComprobante = 'FACTURA'): FacturaNotaVenta
    {
        $total = $poliza->primaAnual()->monto();
        $tasaImpuesto = strtoupper($tipoComprobante) === 'FACTURA' ? 0.13 : 0.00;
        $impuestos = round($total * $tasaImpuesto, 2);
        $subtotal = round($total - $impuestos, 2);

        $comprobanteVO = NumeroComprobanteFiscal::generarNuevo($tipoComprobante);
        $id = UuidId::generate();

        $urlPdf = sprintf('http://localhost:8001/api/v1/facturas/%s/pdf', $id->value());
        $hashDigital = hash('sha256', implode('|', [
            $id->value(),
            $comprobanteVO->numeroFactura(),
            $poliza->numeroPoliza(),
            $total,
            gmdate('Y-m-d\TH:i:s\Z'),
        ]));

        return new FacturaNotaVenta(
            $id,
            $comprobanteVO,
            $poliza->id(),
            $poliza->clienteId(),
            $subtotal,
            $impuestos,
            $total,
            $poliza->primaAnual()->moneda(),
            'EMITIDA',
            $urlPdf,
            $hashDigital
        );
    }
}

