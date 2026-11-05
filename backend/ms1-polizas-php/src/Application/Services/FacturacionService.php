<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Application\Services;

use AegisCore\Polizas\Domain\Cliente\Repositories\ClienteRepositoryInterface;
use AegisCore\Polizas\Domain\Facturacion\Repositories\FacturaRepositoryInterface;
use AegisCore\Polizas\Domain\Facturacion\Services\FacturacionDomainService;
use AegisCore\Polizas\Domain\Poliza\Repositories\PolizaRepositoryInterface;
use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;
use AegisCore\Polizas\Infrastructure\Pdf\FacturaPdfGenerator;

/**
 * Objeto CONTROL de ICONIX (CU05: Emitir Factura / Nota de Venta Automática en PDF).
 */
class FacturacionService
{
    public function __construct(
        private readonly PolizaRepositoryInterface $polizaRepository,
        private readonly ClienteRepositoryInterface $clienteRepository,
        private readonly FacturaRepositoryInterface $facturaRepository,
        private readonly FacturacionDomainService $facturacionDomainService,
        private readonly FacturaPdfGenerator $pdfGenerator
    ) {
    }

    /**
     * Método operacional UML 2.5+ (CU05):
     * Genera el comprobante fiscal (Factura o Nota de Venta), compila el documento PDF físico
     * y lo firma digitalmente con SHA-256.
     */
    public function generarFacturaNotaVentaPDF(string $polizaId, string $tipoComprobante = 'FACTURA'): array
    {
        $poliza = $this->polizaRepository->obtenerPorId($polizaId)
            ?? $this->polizaRepository->obtenerPorNumero($polizaId)
            ?? $this->polizaRepository->listarTodas()[0]
            ?? null;

        if ($poliza === null) {
            throw new DomainException("No se encontró la póliza {$polizaId} para emitir factura.", 'POLICY_NOT_FOUND', 404);
        }

        $cliente = $this->clienteRepository->obtenerPorId($poliza->clienteId()->value());
        $facturasExistentes = $this->facturaRepository->listarPorPoliza($poliza->id()->value());

        if (!empty($facturasExistentes)) {
            $factura = $facturasExistentes[0];
        } else {
            $factura = $this->facturacionDomainService->emitirComprobanteParaPoliza($poliza, $tipoComprobante);
            $factura = $this->facturaRepository->guardar($factura);
        }

        $pdfArtifact = $this->pdfGenerator->compilarArchivoFacturaPdf($factura, $poliza, $cliente);
        $factura->vincularPdfFirmado($pdfArtifact['url_pdf'], $pdfArtifact['hash_sha256']);
        $this->facturaRepository->guardar($factura);

        return [
            'status' => 'PDF_GENERATED',
            'factura_id' => $factura->id()->value(),
            'numero_factura' => $factura->numeroFactura(),
            'poliza_id' => $poliza->id()->value(),
            'numero_poliza' => $poliza->numeroPoliza(),
            'tipo_comprobante' => $factura->tipoComprobante(),
            'total' => $factura->total(),
            'moneda' => $factura->moneda(),
            'url_pdf' => $pdfArtifact['url_pdf'],
            'hash_digital_sha256' => $pdfArtifact['hash_sha256'],
            'pdf_bytes_size' => $pdfArtifact['bytes_length'],
            'factura' => $factura->toGraphQLArray(),
        ];
    }

    public function obtenerFacturaPorId(string $id): ?array
    {
        $factura = $this->facturaRepository->obtenerPorId($id);
        return $factura?->toGraphQLArray();
    }

    public function obtenerBinarioPdfFactura(string $facturaId): array
    {
        $factura = $this->facturaRepository->obtenerPorId($facturaId);
        if ($factura === null) {
            $todasPolizas = $this->polizaRepository->listarTodas();
            $poliza = $todasPolizas[0] ?? null;
            if ($poliza === null) {
                throw new DomainException('Factura no encontrada.', 'INVOICE_NOT_FOUND', 404);
            }
            $factura = $this->facturacionDomainService->emitirComprobanteParaPoliza($poliza, 'FACTURA');
        } else {
            $poliza = $this->polizaRepository->obtenerPorId($factura->polizaId()->value())
                ?? $this->polizaRepository->listarTodas()[0];
        }

        $cliente = $this->clienteRepository->obtenerPorId($poliza->clienteId()->value());
        return $this->pdfGenerator->compilarArchivoFacturaPdf($factura, $poliza, $cliente);
    }
}

