<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Application\Services;

use AegisCore\Polizas\Domain\Catalogo\Entities\Cobertura;
use AegisCore\Polizas\Domain\Catalogo\Entities\PlanSeguro;
use AegisCore\Polizas\Domain\Catalogo\Repositories\PlanSeguroRepositoryInterface;
use AegisCore\Polizas\Domain\Catalogo\ValueObjects\TipoPlanVO;
use AegisCore\Polizas\Domain\Cliente\Entities\Cliente;
use AegisCore\Polizas\Domain\Cliente\Repositories\ClienteRepositoryInterface;
use AegisCore\Polizas\Domain\Cliente\ValueObjects\DocumentoIdentidad;
use AegisCore\Polizas\Domain\Cliente\ValueObjects\PerfilRiesgoCliente;
use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;
use AegisCore\Polizas\Domain\Shared\ValueObjects\PrimaMonetaria;
use AegisCore\Polizas\Domain\Shared\ValueObjects\UuidId;

/**
 * Objeto CONTROL de ICONIX (CU03: Gestionar Catálogo de Planes de Seguro, Coberturas y Clientes).
 * Orquesta los Agregados y Servicios de Dominio DDD con relaciones de Clave Foránea (FK).
 */
class CatalogoPolizaApplicationService
{
    public function __construct(
        private readonly PlanSeguroRepositoryInterface $planRepository,
        private readonly ClienteRepositoryInterface $clienteRepository
    ) {
    }

    /**
     * Método operacional UML 2.5+ (CU03):
     * Lista el catálogo de planes de seguro junto a sus coberturas vinculadas por FK.
     */
    public function listarPlanesSeguro(?string $tipo = null): array
    {
        $planes = $this->planRepository->listarPlanes($tipo);
        return array_map(fn(PlanSeguro $p) => $p->toGraphQLArray(), $planes);
    }

    /**
     * Método operacional UML 2.5+ (CU03):
     * Registra un nuevo PlanSeguro y sus Coberturas en PostgreSQL respetando invariantes DDD.
     */
    public function registrarPlanSeguroDDD(array $input): array
    {
        $planId = isset($input['id']) && trim((string)$input['id']) !== ''
            ? new UuidId((string)$input['id'])
            : UuidId::generate();

        $codigo = strtoupper(trim((string)($input['codigo'] ?? 'PLAN-CUSTOM-' . random_int(100, 999))));
        $nombre = trim((string)($input['nombre'] ?? 'Plan Seguro Personalizado'));
        $tipoVO = new TipoPlanVO((string)($input['tipo'] ?? 'VEHICULAR'));
        $primaVO = new PrimaMonetaria((float)($input['primaBaseAnual'] ?? 500.00), 'USD');
        $deducible = (float)($input['deducibleBasePorcentaje'] ?? 10.0);
        $descripcion = isset($input['descripcion']) ? (string)$input['descripcion'] : null;

        $coberturasEntities = [];
        $coberturasInput = (array)($input['coberturas'] ?? []);
        foreach ($coberturasInput as $cobData) {
            $coberturasEntities[] = new Cobertura(
                UuidId::generate(),
                $planId,
                (string)($cobData['codigo'] ?? 'COB-GEN-' . random_int(10, 99)),
                (string)($cobData['nombre'] ?? 'Cobertura General'),
                (float)($cobData['sumaAseguradaMax'] ?? 20000.00),
                (float)($cobData['deducibleMinimo'] ?? 150.00),
                (float)($cobData['deduciblePorcentaje'] ?? $deducible),
                isset($cobData['descripcion']) ? (string)$cobData['descripcion'] : null,
                (bool)($cobData['obligatoria'] ?? true)
            );
        }

        if (empty($coberturasEntities)) {
            $coberturasEntities[] = new Cobertura(
                UuidId::generate(),
                $planId,
                'COB-BASE-' . substr($codigo, -4),
                'Cobertura Principal Integral',
                25000.00,
                150.00,
                $deducible,
                'Cobertura base creada automáticamente con el plan.',
                true
            );
        }

        $plan = new PlanSeguro(
            $planId,
            $codigo,
            $nombre,
            $tipoVO,
            $primaVO,
            $deducible,
            $descripcion,
            (bool)($input['activo'] ?? true),
            $coberturasEntities
        );

        $guardado = $this->planRepository->guardarPlan($plan);
        return $guardado->toGraphQLArray();
    }

    /**
     * Método operacional UML 2.5+ (CU03):
     * Agrega una nueva Cobertura con FK hacia un PlanSeguro existente.
     */
    public function agregarCoberturaAPlan(array $input): array
    {
        $planIdStr = (string)($input['planId'] ?? '');
        $plan = $this->planRepository->obtenerPorId($planIdStr);
        if ($plan === null) {
            throw new DomainException("El PlanSeguro con ID {$planIdStr} no existe.", 'PLAN_NOT_FOUND', 404);
        }

        $cobertura = new Cobertura(
            UuidId::generate(),
            $plan->id(),
            (string)($input['codigo'] ?? 'COB-EXTRA-' . random_int(100, 999)),
            (string)($input['nombre'] ?? 'Cobertura Adicional'),
            (float)($input['sumaAseguradaMax'] ?? 15000.00),
            (float)($input['deducibleMinimo'] ?? 100.00),
            (float)($input['deduciblePorcentaje'] ?? 10.00),
            isset($input['descripcion']) ? (string)$input['descripcion'] : null,
            (bool)($input['obligatoria'] ?? false)
        );

        $guardada = $this->planRepository->guardarCobertura($cobertura);
        return $guardada->toGraphQLArray();
    }

    /**
     * Método operacional UML 2.5+ (CU03):
     * Registra o actualiza un Cliente en el Core ERP.
     */
    public function registrarClienteDDD(array $input): array
    {
        $docVO = new DocumentoIdentidad(
            (string)($input['tipoDocumento'] ?? 'CI'),
            (string)($input['numeroDocumento'] ?? '')
        );

        $existente = $this->clienteRepository->buscarPorDocumento($docVO->numeroDocumento());
        $id = $existente ? $existente->id() : UuidId::generate();

        $perfilVO = new PerfilRiesgoCliente(
            (int)($input['scoreCrediticio'] ?? 780),
            isset($input['perfilRiesgo']) ? (string)$input['perfilRiesgo'] : null
        );

        $cliente = new Cliente(
            $id,
            $docVO,
            (string)($input['nombres'] ?? ''),
            (string)($input['apellidos'] ?? ''),
            (string)($input['email'] ?? ''),
            (string)($input['telefono'] ?? ''),
            isset($input['direccion']) ? (string)$input['direccion'] : null,
            (string)($input['ciudad'] ?? 'Santa Cruz'),
            $perfilVO,
            isset($input['usuarioId']) ? (string)$input['usuarioId'] : null
        );

        $guardado = $this->clienteRepository->guardar($cliente);
        return $guardado->toGraphQLArray();
    }

    public function obtenerClientePorId(string $id): ?array
    {
        $cliente = $this->clienteRepository->obtenerPorId($id);
        return $cliente?->toGraphQLArray();
    }

    public function buscarClientePorDocumento(string $documento): ?array
    {
        $cliente = $this->clienteRepository->buscarPorDocumento($documento);
        return $cliente?->toGraphQLArray();
    }

    public function listarClientes(): array
    {
        return array_map(
            fn(Cliente $c) => $c->toGraphQLArray(),
            $this->clienteRepository->listarTodos()
        );
    }
}

