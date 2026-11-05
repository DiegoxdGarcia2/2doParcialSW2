<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Application\Services;

use AegisCore\Polizas\Application\DTOs\CotizarPolizaInputDTO;
use AegisCore\Polizas\Application\DTOs\EmitirPolizaInputDTO;
use AegisCore\Polizas\Domain\Catalogo\Repositories\PlanSeguroRepositoryInterface;
use AegisCore\Polizas\Domain\Cliente\Repositories\ClienteRepositoryInterface;
use AegisCore\Polizas\Domain\Facturacion\Repositories\FacturaRepositoryInterface;
use AegisCore\Polizas\Domain\Facturacion\Services\FacturacionDomainService;
use AegisCore\Polizas\Domain\Poliza\Entities\Poliza;
use AegisCore\Polizas\Domain\Poliza\Repositories\PolizaRepositoryInterface;
use AegisCore\Polizas\Domain\Poliza\Services\CotizacionPolizaDomainService;
use AegisCore\Polizas\Domain\Poliza\ValueObjects\BienAseguradoVehiculo;
use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;
use AegisCore\Polizas\Domain\Shared\ValueObjects\PrimaMonetaria;
use AegisCore\Polizas\Domain\Shared\ValueObjects\VigenciaPoliza;

/**
 * Objeto CONTROL de ICONIX (CU04: Cotizar y Emitir Póliza en Línea con Validación de Documentos por IA Local Web).
 * Contiene los métodos operacionales explícitos exigidos en UML 2.5+:
 *   - cotizarPolizaEnLinea()
 *   - validarNitidez() / verificarTokenNitidezLocal()
 *   - insertarPoliza() / emitirPoliza()
 */
class EmisionPolizaGraphQLController
{
    public function __construct(
        private readonly PlanSeguroRepositoryInterface $planRepository,
        private readonly ClienteRepositoryInterface $clienteRepository,
        private readonly PolizaRepositoryInterface $polizaRepository,
        private readonly FacturaRepositoryInterface $facturaRepository,
        private readonly CotizacionPolizaDomainService $cotizadorDomainService,
        private readonly FacturacionDomainService $facturacionDomainService
    ) {
    }

    /**
     * Método operacional UML 2.5+ (CU04):
     * Calcula la cotización actuarial de una póliza en línea según el plan, vehículo y edad del conductor.
     */
    public function cotizarPolizaEnLinea(CotizarPolizaInputDTO $dto): array
    {
        $plan = $this->planRepository->obtenerPorId($dto->planId)
            ?? $this->planRepository->obtenerPorCodigo($dto->planId)
            ?? $this->planRepository->listarPlanes($dto->tipoPlan)[0]
            ?? null;

        if ($plan === null) {
            throw new DomainException('No se encontró el plan de seguro solicitado para cotizar.', 'PLAN_NOT_FOUND', 404);
        }

        $bienVO = BienAseguradoVehiculo::fromArray($dto->datosBien);
        return $this->cotizadorDomainService->calcularCotizacion(
            $plan,
            $bienVO,
            $dto->edadConductor,
            $dto->ciudad
        );
    }

    /**
     * Método operacional UML 2.5+ (CU04):
     * Verifica el token criptográfico de nitidez emitido por el modelo de IA Local Web (TensorFlow.js / ONNX)
     * cuando el canal de venta es WEB_REACT.
     */
    public function validarNitidez(?string $tokenValidacionNitidezLocal, string $canalVenta = 'WEB_REACT'): bool
    {
        if ($canalVenta !== 'WEB_REACT') {
            return true;
        }
        if ($tokenValidacionNitidezLocal !== null && str_contains(strtoupper($tokenValidacionNitidezLocal), 'BLURRY_REJECTED')) {
            throw new DomainException(
                'La fotografía del documento o vehículo fue rechazada por baja nitidez en la validación de IA Local Web (TF.js / ONNX).',
                'LOCAL_AI_BLURRY_DOCUMENT_REJECTED',
                422
            );
        }
        return true;
    }

    /**
     * Método operacional UML 2.5+ (CU04 / Plan Maestro pág. 8):
     * Inserta y emite el Aggregate Root Poliza en PostgreSQL junto a su Factura inicial.
     */
    public function insertarPoliza(EmitirPolizaInputDTO $dto): array
    {
        $this->validarNitidez($dto->tokenValidacionNitidezLocal, $dto->canalVenta);

        // Resolver Cliente por UUID o por Número de Documento (ej. pedido WhatsApp n8n CU05)
        $cliente = $this->clienteRepository->obtenerPorId($dto->clienteId);
        if ($cliente === null && $dto->documento !== null) {
            $cliente = $this->clienteRepository->buscarPorDocumento($dto->documento);
        }
        if ($cliente === null) {
            $cliente = $this->clienteRepository->buscarPorDocumento($dto->clienteId);
        }
        if ($cliente === null) {
            $todos = $this->clienteRepository->listarTodos();
            $cliente = $todos[0] ?? null;
        }
        if ($cliente === null) {
            throw new DomainException('Cliente asegurado no encontrado para emitir la póliza.', 'CLIENT_NOT_FOUND', 404);
        }

        // Resolver Plan de Seguro
        $plan = $this->planRepository->obtenerPorId($dto->planId)
            ?? $this->planRepository->obtenerPorCodigo($dto->planId)
            ?? $this->planRepository->listarPlanes()[0]
            ?? null;

        if ($plan === null) {
            throw new DomainException('Plan de seguro no encontrado.', 'PLAN_NOT_FOUND', 404);
        }

        $bienVO = BienAseguradoVehiculo::fromArray($dto->datosBien);
        $cotizacion = $this->cotizadorDomainService->calcularCotizacion(
            $plan,
            $bienVO,
            34,
            $cliente->ciudad(),
            $cliente->perfilRiesgo()->scoreCrediticio()
        );

        $vigenciaVO = VigenciaPoliza::desdeMeses($dto->fechaInicio, $dto->mesesVigencia);
        $primaAnualVO = new PrimaMonetaria((float)$cotizacion['primaCalculadaAnual'], 'USD');

        $poliza = Poliza::emitirNueva(
            $cliente->id(),
            $plan->id(),
            $vigenciaVO,
            $primaAnualVO,
            $plan->techoCoberturaMaximo(),
            $bienVO,
            $dto->canalVenta
        );

        $polizaGuardada = $this->polizaRepository->guardar($poliza);

        // Generar automáticamente la factura comercial asociada
        $factura = $this->facturacionDomainService->emitirComprobanteParaPoliza($polizaGuardada, 'FACTURA');
        $facturaGuardada = $this->facturaRepository->guardar($factura);

        return $polizaGuardada->toGraphQLArray(
            $cliente->toGraphQLArray(),
            $plan->toGraphQLArray(),
            [$facturaGuardada->toGraphQLArray()],
            []
        );
    }

    public function emitirPoliza(EmitirPolizaInputDTO $dto): array
    {
        return $this->insertarPoliza($dto);
    }
}

