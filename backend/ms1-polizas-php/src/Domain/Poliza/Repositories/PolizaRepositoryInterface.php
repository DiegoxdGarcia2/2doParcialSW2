<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Poliza\Repositories;

use AegisCore\Polizas\Domain\Poliza\Entities\Poliza;

/**
 * Repositorio de Dominio DDD: PolizaRepositoryInterface.
 */
interface PolizaRepositoryInterface
{
    public function obtenerPorId(string $id): ?Poliza;

    public function obtenerPorNumero(string $numeroPoliza): ?Poliza;

    /**
     * @return Poliza[]
     */
    public function listarPorCliente(string $clienteId): array;

    /**
     * @return Poliza[]
     */
    public function listarTodas(): array;

    public function guardar(Poliza $poliza): Poliza;
}

