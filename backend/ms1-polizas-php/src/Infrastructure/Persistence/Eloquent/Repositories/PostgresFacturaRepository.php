<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Infrastructure\Persistence\Eloquent\Repositories;

use AegisCore\Polizas\Domain\Facturacion\Entities\FacturaNotaVenta;
use AegisCore\Polizas\Domain\Facturacion\Repositories\FacturaRepositoryInterface;
use AegisCore\Polizas\Domain\Facturacion\ValueObjects\NumeroComprobanteFiscal;
use AegisCore\Polizas\Domain\Shared\ValueObjects\UuidId;
use AegisCore\Polizas\Infrastructure\Persistence\Eloquent\PdoPostgresConnection;
use Throwable;

/**
 * Repositorio de Infraestructura PostgreSQL (Eloquent/PDO): PostgresFacturaRepository.
 */
class PostgresFacturaRepository implements FacturaRepositoryInterface
{
    public function __construct(
        private readonly PdoPostgresConnection $connection
    ) {
    }

    public function obtenerPorId(string $id): ?FacturaNotaVenta
    {
        $pdo = $this->connection->getPdo();
        if ($pdo !== null) {
            try {
                $stmt = $pdo->prepare('SELECT * FROM factura_nota_venta WHERE id::text = :id OR numero_factura = :num LIMIT 1');
                $stmt->execute(['id' => $id, 'num' => $id]);
                $row = $stmt->fetch();
                if (is_array($row)) {
                    return $this->mapRowToEntity($row);
                }
            } catch (Throwable) {
                // Fallback
            }
        }

        $state = $this->connection->readState();
        if (isset($state['facturas'][$id])) {
            return $this->mapRowToEntity($state['facturas'][$id]);
        }
        foreach ($state['facturas'] as $row) {
            if ((string)$row['numero_factura'] === $id) {
                return $this->mapRowToEntity($row);
            }
        }
        return null;
    }

    public function listarPorPoliza(string $polizaId): array
    {
        $pdo = $this->connection->getPdo();
        if ($pdo !== null) {
            try {
                $stmt = $pdo->prepare('SELECT * FROM factura_nota_venta WHERE poliza_id::text = :pid ORDER BY fecha_emision DESC');
                $stmt->execute(['pid' => $polizaId]);
                $rows = $stmt->fetchAll();
                if (!empty($rows)) {
                    return array_map(fn(array $r) => $this->mapRowToEntity($r), $rows);
                }
            } catch (Throwable) {
                // Fallback
            }
        }

        $state = $this->connection->readState();
        $result = [];
        foreach ($state['facturas'] as $row) {
            if ((string)$row['poliza_id'] === $polizaId) {
                $result[] = $this->mapRowToEntity($row);
            }
        }
        return $result;
    }

    public function listarPorCliente(string $clienteId): array
    {
        $pdo = $this->connection->getPdo();
        if ($pdo !== null) {
            try {
                $stmt = $pdo->prepare('SELECT * FROM factura_nota_venta WHERE cliente_id::text = :cid ORDER BY fecha_emision DESC');
                $stmt->execute(['cid' => $clienteId]);
                $rows = $stmt->fetchAll();
                if (!empty($rows)) {
                    return array_map(fn(array $r) => $this->mapRowToEntity($r), $rows);
                }
            } catch (Throwable) {
                // Fallback
            }
        }

        $state = $this->connection->readState();
        $result = [];
        foreach ($state['facturas'] as $row) {
            if ((string)$row['cliente_id'] === $clienteId) {
                $result[] = $this->mapRowToEntity($row);
            }
        }
        return $result;
    }

    public function guardar(FacturaNotaVenta $factura): FacturaNotaVenta
    {
        $id = $factura->id()->value();
        $row = [
            'id' => $id,
            'numero_factura' => $factura->numeroFactura(),
            'poliza_id' => $factura->polizaId()->value(),
            'cliente_id' => $factura->clienteId()->value(),
            'tipo_comprobante' => $factura->tipoComprobante(),
            'fecha_emision' => $factura->fechaEmision(),
            'subtotal' => $factura->subtotal(),
            'impuestos' => $factura->impuestos(),
            'total' => $factura->total(),
            'moneda' => $factura->moneda(),
            'estado' => $factura->estado(),
            'url_pdf_almacenado' => $factura->urlPdfAlmacenado(),
            'hash_digital_sha256' => $factura->hashDigitalSha256(),
        ];

        $pdo = $this->connection->getPdo(true);
        if ($pdo !== null) {
            try {
                $sql = <<<SQL
                INSERT INTO factura_nota_venta (
                    id, numero_factura, poliza_id, cliente_id, tipo_comprobante,
                    subtotal, impuestos, total, moneda, estado, url_pdf_almacenado, hash_digital_sha256
                ) VALUES (
                    :id, :numero_factura, :poliza_id, :cliente_id, :tipo_comprobante,
                    :subtotal, :impuestos, :total, :moneda, :estado, :url_pdf_almacenado, :hash_digital_sha256
                )
                ON CONFLICT (id) DO UPDATE SET
                    url_pdf_almacenado = EXCLUDED.url_pdf_almacenado,
                    hash_digital_sha256 = EXCLUDED.hash_digital_sha256,
                    estado = EXCLUDED.estado
                SQL;
                $stmt = $pdo->prepare($sql);
                $stmt->execute([
                    'id' => $row['id'],
                    'numero_factura' => $row['numero_factura'],
                    'poliza_id' => $row['poliza_id'],
                    'cliente_id' => $row['cliente_id'],
                    'tipo_comprobante' => $row['tipo_comprobante'],
                    'subtotal' => $row['subtotal'],
                    'impuestos' => $row['impuestos'],
                    'total' => $row['total'],
                    'moneda' => $row['moneda'],
                    'estado' => $row['estado'],
                    'url_pdf_almacenado' => $row['url_pdf_almacenado'],
                    'hash_digital_sha256' => $row['hash_digital_sha256'],
                ]);
            } catch (Throwable) {
                // Continúa guardando en estado sincronizado
            }
        }

        $state = $this->connection->readState();
        $state['facturas'][$id] = $row;
        $this->connection->writeState($state);

        return $factura;
    }

    private function mapRowToEntity(array $row): FacturaNotaVenta
    {
        return new FacturaNotaVenta(
            new UuidId((string)$row['id']),
            new NumeroComprobanteFiscal(
                (string)$row['numero_factura'],
                (string)($row['tipo_comprobante'] ?? 'FACTURA')
            ),
            new UuidId((string)$row['poliza_id']),
            new UuidId((string)$row['cliente_id']),
            (float)$row['subtotal'],
            (float)$row['impuestos'],
            (float)$row['total'],
            (string)($row['moneda'] ?? 'USD'),
            (string)($row['estado'] ?? 'EMITIDA'),
            isset($row['url_pdf_almacenado']) ? (string)$row['url_pdf_almacenado'] : null,
            isset($row['hash_digital_sha256']) ? (string)$row['hash_digital_sha256'] : null,
            (string)($row['fecha_emision'] ?? gmdate('Y-m-d\TH:i:s\Z'))
        );
    }
}

