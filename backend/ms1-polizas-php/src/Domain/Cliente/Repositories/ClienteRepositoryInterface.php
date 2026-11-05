<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Cliente\Repositories;

use AegisCore\Polizas\Domain\Cliente\Entities\Cliente;

/**
 * Repositorio de Dominio DDD: ClienteRepositoryInterface.
 */
interface ClienteRepositoryInterface
{
    public function obtenerPorId(string $id): ?Cliente;

    public function buscarPorDocumento(string $numeroDocumento): ?Cliente;

    /**
     * @return Cliente[]
     */
    public function listarTodos(): array;

    public function guardar(Cliente $cliente): Cliente;
}

