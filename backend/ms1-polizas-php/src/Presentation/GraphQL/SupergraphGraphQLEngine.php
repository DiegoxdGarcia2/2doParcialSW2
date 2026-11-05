<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Presentation\GraphQL;

use AegisCore\Polizas\Application\DTOs\CotizarPolizaInputDTO;
use AegisCore\Polizas\Application\DTOs\EmitirPolizaInputDTO;
use AegisCore\Polizas\Application\Services\ApolloFederationResolver;
use AegisCore\Polizas\Application\Services\CatalogoPolizaApplicationService;
use AegisCore\Polizas\Application\Services\EmisionPolizaGraphQLController;
use AegisCore\Polizas\Application\Services\FacturacionService;
use AegisCore\Polizas\Domain\Catalogo\Repositories\PlanSeguroRepositoryInterface;
use AegisCore\Polizas\Domain\Cliente\Repositories\ClienteRepositoryInterface;
use AegisCore\Polizas\Domain\Facturacion\Repositories\FacturaRepositoryInterface;
use AegisCore\Polizas\Domain\Poliza\Repositories\PolizaRepositoryInterface;
use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;
use Throwable;

/**
 * Motor GraphQL Federado de MS1 (Presentation Layer - DDD).
 * Implementa íntegramente el contrato congelado contracts/supergraph.graphql
 * para CU02, CU03, CU04 y CU05.
 */
class SupergraphGraphQLEngine
{
    public function __construct(
        private readonly ApolloFederationResolver $federationResolver,
        private readonly CatalogoPolizaApplicationService $catalogoService,
        private readonly EmisionPolizaGraphQLController $emisionController,
        private readonly FacturacionService $facturacionService,
        private readonly PolizaRepositoryInterface $polizaRepository,
        private readonly ClienteRepositoryInterface $clienteRepository,
        private readonly PlanSeguroRepositoryInterface $planRepository,
        private readonly FacturaRepositoryInterface $facturaRepository
    ) {
    }

    public function execute(string $query, array $variables = [], ?string $operationName = null): array
    {
        $trimmed = trim($query);
        if ($trimmed === '') {
            return [
                'errors' => [['message' => 'La consulta GraphQL no puede estar vacía.']],
            ];
        }

        try {
            $data = [];

            // 1. Introspección básica (__typename / __schema)
            if (str_contains($trimmed, '__schema') || str_contains($trimmed, '__type')) {
                $data['__schema'] = [
                    'queryType' => ['name' => 'Query'],
                    'mutationType' => ['name' => 'Mutation'],
                    'types' => [
                        ['name' => 'Cliente'],
                        ['name' => 'PlanSeguro'],
                        ['name' => 'Cobertura'],
                        ['name' => 'Poliza'],
                        ['name' => 'FacturaNotaVenta'],
                        ['name' => 'ExpedienteSiniestro'],
                        ['name' => 'ResumenUnificadoPayload'],
                        ['name' => 'CotizacionResultado'],
                    ],
                ];
            }

            // 2. CU02: resumenUnificadoAsegurado(clienteId: ID!)
            if (preg_match('/\bresumenUnificadoAsegurado\b/', $trimmed)) {
                $clienteId = $this->extractArgument($trimmed, 'resumenUnificadoAsegurado', 'clienteId', $variables)
                    ?? 'b0000001-0000-0000-0000-000000000001';
                $data['resumenUnificadoAsegurado'] = $this->federationResolver->resolverResumenUnificadoAsegurado((string)$clienteId);
            }

            // 3. CU03: listarPlanesSeguro(tipo: TipoPlan)
            if (preg_match('/\blistarPlanesSeguro\b/', $trimmed)) {
                $tipo = $this->extractArgument($trimmed, 'listarPlanesSeguro', 'tipo', $variables);
                $data['listarPlanesSeguro'] = $this->catalogoService->listarPlanesSeguro(
                    is_string($tipo) && $tipo !== '' ? $tipo : null
                );
            }

            // 4. CU03: listarClientes (Extensión administrativa ERP)
            if (preg_match('/\blistarClientes\b/', $trimmed)) {
                $data['listarClientes'] = $this->catalogoService->listarClientes();
            }

            // 5. obtenerClientePorId(id: ID!)
            if (preg_match('/\bobtenerClientePorId\b/', $trimmed)) {
                $id = $this->extractArgument($trimmed, 'obtenerClientePorId', 'id', $variables)
                    ?? 'b0000001-0000-0000-0000-000000000001';
                $data['obtenerClientePorId'] = $this->catalogoService->obtenerClientePorId((string)$id);
            }

            // 6. buscarClientePorDocumento(documento: String!)
            if (preg_match('/\bbuscarClientePorDocumento\b/', $trimmed)) {
                $doc = $this->extractArgument($trimmed, 'buscarClientePorDocumento', 'documento', $variables)
                    ?? '6234891-SC';
                $data['buscarClientePorDocumento'] = $this->catalogoService->buscarClientePorDocumento((string)$doc);
            }

            // 7. obtenerPolizaPorNumero(numeroPoliza: String!)
            if (preg_match('/\bobtenerPolizaPorNumero\b/', $trimmed)) {
                $num = $this->extractArgument($trimmed, 'obtenerPolizaPorNumero', 'numeroPoliza', $variables)
                    ?? 'POL-2026-AUT-00892';
                $poliza = $this->polizaRepository->obtenerPorNumero((string)$num);
                $data['obtenerPolizaPorNumero'] = $poliza ? $this->hydratePoliza($poliza) : null;
            }

            // 8. listarPolizasPorCliente(clienteId: ID!)
            if (preg_match('/\blistarPolizasPorCliente\b/', $trimmed)) {
                $cid = $this->extractArgument($trimmed, 'listarPolizasPorCliente', 'clienteId', $variables)
                    ?? 'b0000001-0000-0000-0000-000000000001';
                $polizas = $this->polizaRepository->listarPorCliente((string)$cid);
                $data['listarPolizasPorCliente'] = array_map(fn($p) => $this->hydratePoliza($p), $polizas);
            }

            // 9. obtenerFactura(id: ID!)
            if (preg_match('/\bobtenerFactura\b/', $trimmed)) {
                $fid = $this->extractArgument($trimmed, 'obtenerFactura', 'id', $variables)
                    ?? 'f0000001-0000-0000-0000-000000000001';
                $data['obtenerFactura'] = $this->facturacionService->obtenerFacturaPorId((string)$fid);
            }

            // 10. MUTATION CU04: cotizarPolizaEnLinea(input: CotizarPolizaInput!)
            if (preg_match('/\bcotizarPolizaEnLinea\b/', $trimmed)) {
                $inputArr = $this->extractInputObject($trimmed, 'cotizarPolizaEnLinea', $variables);
                $dto = CotizarPolizaInputDTO::fromArray($inputArr);
                $data['cotizarPolizaEnLinea'] = $this->emisionController->cotizarPolizaEnLinea($dto);
            }

            // 11. MUTATION CU04 / CU05: emitirPoliza(input: EmitirPolizaInput!)
            if (preg_match('/\bemitirPoliza\b/', $trimmed)) {
                $inputArr = $this->extractInputObject($trimmed, 'emitirPoliza', $variables);
                $dto = EmitirPolizaInputDTO::fromArray($inputArr);
                $data['emitirPoliza'] = $this->emisionController->insertarPoliza($dto);
            }

            // 12. MUTATION CU03: registrarPlanSeguro(input: ...)
            if (preg_match('/\bregistrarPlanSeguro\b/', $trimmed)) {
                $inputArr = $this->extractInputObject($trimmed, 'registrarPlanSeguro', $variables);
                $data['registrarPlanSeguro'] = $this->catalogoService->registrarPlanSeguroDDD($inputArr);
            }

            // 13. MUTATION CU03: agregarCoberturaPlan(input: ...)
            if (preg_match('/\bagregarCoberturaPlan\b/', $trimmed)) {
                $inputArr = $this->extractInputObject($trimmed, 'agregarCoberturaPlan', $variables);
                $data['agregarCoberturaPlan'] = $this->catalogoService->agregarCoberturaAPlan($inputArr);
            }

            // 14. MUTATION CU03: registrarCliente(input: ...)
            if (preg_match('/\bregistrarCliente\b/', $trimmed)) {
                $inputArr = $this->extractInputObject($trimmed, 'registrarCliente', $variables);
                $data['registrarCliente'] = $this->catalogoService->registrarClienteDDD($inputArr);
            }

            if (empty($data)) {
                $data = [
                    'service' => 'ms1-polizas-php',
                    'pattern' => 'Domain-Driven Design (DDD)',
                    'status' => 'SUPERGRAPH_ACTIVE',
                ];
            }

            return ['data' => $data];
        } catch (DomainException $e) {
            return [
                'errors' => [
                    [
                        'message' => $e->getMessage(),
                        'extensions' => [
                            'code' => $e->getErrorCode(),
                            'classification' => 'DomainException',
                        ],
                    ],
                ],
            ];
        } catch (Throwable $e) {
            return [
                'errors' => [
                    [
                        'message' => $e->getMessage(),
                        'extensions' => [
                            'code' => 'INTERNAL_GRAPHQL_ERROR',
                        ],
                    ],
                ],
            ];
        }
    }

    private function hydratePoliza(\AegisCore\Polizas\Domain\Poliza\Entities\Poliza $poliza): array
    {
        $cliente = $this->clienteRepository->obtenerPorId($poliza->clienteId()->value());
        $plan = $this->planRepository->obtenerPorId($poliza->planId()->value());
        $facturas = array_map(
            fn($f) => $f->toGraphQLArray(),
            $this->facturaRepository->listarPorPoliza($poliza->id()->value())
        );
        $siniestros = $this->federationResolver->federarExpedientesSiniestrosMongoDB(
            $poliza->id()->value(),
            $poliza->numeroPoliza()
        );

        return $poliza->toGraphQLArray(
            $cliente?->toGraphQLArray(),
            $plan?->toGraphQLArray(),
            $facturas,
            $siniestros
        );
    }

    private function extractArgument(string $query, string $fieldName, string $argName, array $variables): mixed
    {
        if (isset($variables[$argName])) {
            return $variables[$argName];
        }

        $pattern = sprintf('/%s\s*\([^)]*%s\s*:\s*(\$[a-zA-Z0-9_]+|"[^"]*"|\'[^\']*\'|[a-zA-Z0-9_\-]+)/s', preg_quote($fieldName, '/'), preg_quote($argName, '/'));
        if (preg_match($pattern, $query, $matches)) {
            $rawVal = trim($matches[1]);
            if (str_starts_with($rawVal, '$')) {
                $varKey = substr($rawVal, 1);
                return $variables[$varKey] ?? null;
            }
            return trim($rawVal, "\"'");
        }

        return null;
    }

    private function extractInputObject(string $query, string $mutationName, array $variables): array
    {
        if (isset($variables['input']) && is_array($variables['input'])) {
            return $variables['input'];
        }

        $result = $variables;

        // Extraer pares clave: valor literales dentro de input: { ... }
        if (preg_match('/' . preg_quote($mutationName, '/') . '\s*\(\s*input\s*:\s*\{(.+)\}\s*\)/s', $query, $m)) {
            $inner = $m[1];
            // Resolver referencias a variables como documento: $doc
            if (preg_match_all('/([a-zA-Z0-9_]+)\s*:\s*(\$[a-zA-Z0-9_]+|"[^"]*"|\'[^\']*\'|[0-9.]+|[A-Z_]+)/', $inner, $pairs, PREG_SET_ORDER)) {
                foreach ($pairs as $pair) {
                    $k = $pair[1];
                    $v = trim($pair[2]);
                    if ($k === 'datosBien') {
                        continue;
                    }
                    if (str_starts_with($v, '$')) {
                        $varName = substr($v, 1);
                        if (isset($variables[$varName])) {
                            $result[$k] = $variables[$varName];
                        }
                    } elseif (is_numeric($v)) {
                        $result[$k] = str_contains($v, '.') ? (float)$v : (int)$v;
                    } else {
                        $result[$k] = trim($v, "\"'");
                    }
                }
            }

            if (preg_match('/datosBien\s*:\s*\{([^}]+)\}/s', $inner, $bienMatch)) {
                $bienInner = $bienMatch[1];
                $datosBien = [];
                if (preg_match_all('/([a-zA-Z0-9_]+)\s*:\s*("[^"]*"|\'[^\']*\'|[0-9.]+)/', $bienInner, $bPairs, PREG_SET_ORDER)) {
                    foreach ($bPairs as $bp) {
                        $bk = $bp[1];
                        $bv = trim($bp[2]);
                        $datosBien[$bk] = is_numeric($bv)
                            ? (str_contains($bv, '.') ? (float)$bv : (int)$bv)
                            : trim($bv, "\"'");
                    }
                }
                if (!empty($datosBien)) {
                    $result['datosBien'] = $datosBien;
                }
            }
        }

        // Mapear variables directas del flujo n8n ($doc, $placa)
        if (isset($variables['doc']) && !isset($result['documento'])) {
            $result['documento'] = $variables['doc'];
        }
        if (isset($variables['placa']) && !isset($result['placa'])) {
            $result['placa'] = $variables['placa'];
        }

        return $result;
    }
}

