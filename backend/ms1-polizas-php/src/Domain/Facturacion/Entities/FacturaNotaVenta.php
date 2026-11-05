<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Facturacion\Entities;

use AegisCore\Polizas\Domain\Facturacion\ValueObjects\NumeroComprobanteFiscal;
use AegisCore\Polizas\Domain\Shared\ValueObjects\UuidId;

/**
 * Entidad de Dominio DDD: FacturaNotaVenta (Emisión Fiscal / Comercial - CU05 con n8n).
 */
class FacturaNotaVenta
{
    private UuidId $id;
    private NumeroComprobanteFiscal $comprobante;
    private UuidId $polizaId;
    private UuidId $clienteId;
    private string $fechaEmision;
    private float $subtotal;
    private float $impuestos;
    private float $total;
    private string $moneda;
    private string $estado;
    private ?string $urlPdfAlmacenado;
    private ?string $hashDigitalSha256;

    public function __construct(
        UuidId $id,
        NumeroComprobanteFiscal $comprobante,
        UuidId $polizaId,
        UuidId $clienteId,
        float $subtotal,
        float $impuestos,
        float $total,
        string $moneda = 'USD',
        string $estado = 'EMITIDA',
        ?string $urlPdfAlmacenado = null,
        ?string $hashDigitalSha256 = null,
        ?string $fechaEmision = null
    ) {
        $this->id = $id;
        $this->comprobante = $comprobante;
        $this->polizaId = $polizaId;
        $this->clienteId = $clienteId;
        $this->subtotal = round($subtotal, 2);
        $this->impuestos = round($impuestos, 2);
        $this->total = round($total, 2);
        $this->moneda = strtoupper(trim($moneda));
        $this->estado = in_array(strtoupper($estado), ['EMITIDA', 'PAGADA', 'ANULADA'], true)
            ? strtoupper($estado)
            : 'EMITIDA';
        $this->urlPdfAlmacenado = $urlPdfAlmacenado;
        $this->hashDigitalSha256 = $hashDigitalSha256;
        $this->fechaEmision = $fechaEmision ?? gmdate('Y-m-d\TH:i:s\Z');
    }

    public function vincularPdfFirmado(string $urlPdf, string $hashSha256): void
    {
        $this->urlPdfAlmacenado = $urlPdf;
        $this->hashDigitalSha256 = $hashSha256;
    }

    public function id(): UuidId
    {
        return $this->id;
    }

    public function numeroFactura(): string
    {
        return $this->comprobante->numeroFactura();
    }

    public function tipoComprobante(): string
    {
        return $this->comprobante->tipoComprobante();
    }

    public function polizaId(): UuidId
    {
        return $this->polizaId;
    }

    public function clienteId(): UuidId
    {
        return $this->clienteId;
    }

    public function fechaEmision(): string
    {
        return $this->fechaEmision;
    }

    public function subtotal(): float
    {
        return $this->subtotal;
    }

    public function impuestos(): float
    {
        return $this->impuestos;
    }

    public function total(): float
    {
        return $this->total;
    }

    public function moneda(): string
    {
        return $this->moneda;
    }

    public function estado(): string
    {
        return $this->estado;
    }

    public function urlPdfAlmacenado(): ?string
    {
        return $this->urlPdfAlmacenado;
    }

    public function hashDigitalSha256(): ?string
    {
        return $this->hashDigitalSha256;
    }

    public function toGraphQLArray(): array
    {
        return [
            'id' => $this->id->value(),
            'numeroFactura' => $this->numeroFactura(),
            'polizaId' => $this->polizaId->value(),
            'clienteId' => $this->clienteId->value(),
            'tipoComprobante' => $this->tipoComprobante(),
            'fechaEmision' => $this->fechaEmision,
            'subtotal' => $this->subtotal,
            'impuestos' => $this->impuestos,
            'total' => $this->total,
            'moneda' => $this->moneda,
            'estado' => $this->estado,
            'urlPdfAlmacenado' => $this->urlPdfAlmacenado,
            'hashDigitalSha256' => $this->hashDigitalSha256,
        ];
    }
}

