<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Catalogo\Repositories;

use AegisCore\Polizas\Domain\Catalogo\Entities\Cobertura;
use AegisCore\Polizas\Domain\Catalogo\Entities\PlanSeguro;

/**
 * Repositorio de Dominio DDD: PlanSeguroRepositoryInterface (CU03).
 */
interface PlanSeguroRepositoryInterface
{
    /**
     * @return PlanSeguro[]
     */
    public function listarPlanes(?string $tipo = null): array;

    public function obtenerPorId(string $id): ?PlanSeguro;

    public function obtenerPorCodigo(string $codigo): ?PlanSeguro;

    public function guardarPlan(PlanSeguro $plan): PlanSeguro;

    public function guardarCobertura(Cobertura $cobertura): Cobertura;
}

