<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Facturacion\Repositories;

use AegisCore\Polizas\Domain\Facturacion\Entities\FacturaNotaVenta;

/**
 * Repositorio de Dominio DDD: FacturaRepositoryInterface (CU05).
 */
interface FacturaRepositoryInterface
{
    public function obtenerPorId(string $id): ?FacturaNotaVenta;

    /**
     * @return FacturaNotaVenta[]
     */
    public function listarPorPoliza(string $polizaId): array;

    /**
     * @return FacturaNotaVenta[]
     */
    public function listarPorCliente(string $clienteId): array;

    public function guardar(FacturaNotaVenta $factura): FacturaNotaVenta;
}

