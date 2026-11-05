<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Infrastructure\Persistence\Eloquent\Repositories;

use AegisCore\Polizas\Domain\Poliza\Entities\Poliza;
use AegisCore\Polizas\Domain\Poliza\Repositories\PolizaRepositoryInterface;
use AegisCore\Polizas\Domain\Poliza\ValueObjects\BienAseguradoVehiculo;
use AegisCore\Polizas\Domain\Poliza\ValueObjects\EstadoPolizaVO;
use AegisCore\Polizas\Domain\Shared\ValueObjects\PrimaMonetaria;
use AegisCore\Polizas\Domain\Shared\ValueObjects\UuidId;
use AegisCore\Polizas\Domain\Shared\ValueObjects\VigenciaPoliza;
use AegisCore\Polizas\Infrastructure\Persistence\Eloquent\PdoPostgresConnection;
use Throwable;

/**
 * Repositorio de Infraestructura PostgreSQL (Eloquent/PDO): PostgresPolizaRepository.
 * Persiste el Aggregate Root Poliza y su JSONB datos_bien_asegurado.
 */
class PostgresPolizaRepository implements PolizaRepositoryInterface
{
    public function __construct(
        private readonly PdoPostgresConnection $connection
    ) {
    }

    public function obtenerPorId(string $id): ?Poliza
    {
        $pdo = $this->connection->getPdo();
        if ($pdo !== null) {
            try {
                $stmt = $pdo->prepare('SELECT * FROM poliza WHERE id::text = :id LIMIT 1');
                $stmt->execute(['id' => $id]);
                $row = $stmt->fetch();
                if (is_array($row)) {
                    return $this->mapRowToEntity($row);
                }
            } catch (Throwable) {
                // Fallback
            }
        }

        $state = $this->connection->readState();
        if (isset($state['polizas'][$id])) {
            return $this->mapRowToEntity($state['polizas'][$id]);
        }
        return null;
    }

    public function obtenerPorNumero(string $numeroPoliza): ?Poliza
    {
        $numNorm = strtoupper(trim($numeroPoliza));
        $pdo = $this->connection->getPdo();
        if ($pdo !== null) {
            try {
                $stmt = $pdo->prepare('SELECT * FROM poliza WHERE UPPER(numero_poliza) = :num LIMIT 1');
                $stmt->execute(['num' => $numNorm]);
                $row = $stmt->fetch();
                if (is_array($row)) {
                    return $this->mapRowToEntity($row);
                }
            } catch (Throwable) {
                // Fallback
            }
        }

        $state = $this->connection->readState();
        foreach ($state['polizas'] as $row) {
            if (strtoupper((string)$row['numero_poliza']) === $numNorm) {
                return $this->mapRowToEntity($row);
            }
        }
        return null;
    }

    public function listarPorCliente(string $clienteId): array
    {
        $pdo = $this->connection->getPdo();
        if ($pdo !== null) {
            try {
                $stmt = $pdo->prepare('SELECT * FROM poliza WHERE cliente_id::text = :cid ORDER BY created_at DESC');
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
        foreach ($state['polizas'] as $row) {
            if ((string)$row['cliente_id'] === $clienteId) {
                $result[] = $this->mapRowToEntity($row);
            }
        }
        return $result;
    }

    public function listarTodas(): array
    {
        $pdo = $this->connection->getPdo();
        if ($pdo !== null) {
            try {
                $stmt = $pdo->query('SELECT * FROM poliza ORDER BY created_at DESC');
                $rows = $stmt->fetchAll();
                if (!empty($rows)) {
                    return array_map(fn(array $r) => $this->mapRowToEntity($r), $rows);
                }
            } catch (Throwable) {
                // Fallback
            }
        }

        $state = $this->connection->readState();
        return array_values(array_map(fn(array $r) => $this->mapRowToEntity($r), $state['polizas']));
    }

    public function guardar(Poliza $poliza): Poliza
    {
        $id = $poliza->id()->value();
        $row = [
            'id' => $id,
            'numero_poliza' => $poliza->numeroPoliza(),
            'cliente_id' => $poliza->clienteId()->value(),
            'plan_id' => $poliza->planId()->value(),
            'estado' => $poliza->estado()->valor(),
            'fecha_emision' => $poliza->fechaEmision(),
            'fecha_inicio' => $poliza->vigencia()->fechaInicioIso(),
            'fecha_fin' => $poliza->vigencia()->fechaFinIso(),
            'prima_anual' => $poliza->primaAnual()->monto(),
            'prima_mensual' => $poliza->primaMensual()->monto(),
            'moneda' => $poliza->primaAnual()->moneda(),
            'saldo_cobertura_restante' => $poliza->saldoCoberturaRestante()->monto(),
            'datos_bien_asegurado' => $poliza->bienAsegurado()->toDatabaseJson(),
            'canal_venta' => $poliza->canalVenta(),
            'created_at' => $poliza->createdAt(),
            'updated_at' => $poliza->updatedAt(),
        ];

        $pdo = $this->connection->getPdo(true);
        if ($pdo !== null) {
            try {
                $sql = <<<SQL
                INSERT INTO poliza (
                    id, numero_poliza, cliente_id, plan_id, estado, fecha_emision,
                    fecha_inicio, fecha_fin, prima_anual, prima_mensual, moneda,
                    saldo_cobertura_restante, datos_bien_asegurado, canal_venta
                ) VALUES (
                    :id, :numero_poliza, :cliente_id, :plan_id, :estado, :fecha_emision,
                    :fecha_inicio, :fecha_fin, :prima_anual, :prima_mensual, :moneda,
                    :saldo_cobertura_restante, :datos_bien_asegurado::jsonb, :canal_venta
                )
                ON CONFLICT (id) DO UPDATE SET
                    estado = EXCLUDED.estado,
                    saldo_cobertura_restante = EXCLUDED.saldo_cobertura_restante,
                    datos_bien_asegurado = EXCLUDED.datos_bien_asegurado,
                    updated_at = CURRENT_TIMESTAMP
                SQL;
                $stmt = $pdo->prepare($sql);
                $stmt->execute([
                    'id' => $row['id'],
                    'numero_poliza' => $row['numero_poliza'],
                    'cliente_id' => $row['cliente_id'],
                    'plan_id' => $row['plan_id'],
                    'estado' => $row['estado'],
                    'fecha_emision' => substr((string)$row['fecha_emision'], 0, 10),
                    'fecha_inicio' => substr((string)$row['fecha_inicio'], 0, 10),
                    'fecha_fin' => substr((string)$row['fecha_fin'], 0, 10),
                    'prima_anual' => $row['prima_anual'],
                    'prima_mensual' => $row['prima_mensual'],
                    'moneda' => $row['moneda'],
                    'saldo_cobertura_restante' => $row['saldo_cobertura_restante'],
                    'datos_bien_asegurado' => json_encode($row['datos_bien_asegurado']),
                    'canal_venta' => $row['canal_venta'],
                ]);
            } catch (Throwable) {
                // Continúa guardando en estado sincronizado
            }
        }

        $state = $this->connection->readState();
        $state['polizas'][$id] = $row;
        $this->connection->writeState($state);

        return $poliza;
    }

    private function mapRowToEntity(array $row): Poliza
    {
        $bienRaw = $row['datos_bien_asegurado'] ?? [];
        if (is_string($bienRaw)) {
            $bienRaw = json_decode($bienRaw, true) ?? [];
        }
        $moneda = (string)($row['moneda'] ?? 'USD');

        return new Poliza(
            new UuidId((string)$row['id']),
            (string)$row['numero_poliza'],
            new UuidId((string)$row['cliente_id']),
            new UuidId((string)$row['plan_id']),
            new EstadoPolizaVO((string)$row['estado']),
            new VigenciaPoliza((string)$row['fecha_inicio'], (string)$row['fecha_fin']),
            new PrimaMonetaria((float)$row['prima_anual'], $moneda),
            new PrimaMonetaria((float)$row['saldo_cobertura_restante'], $moneda),
            BienAseguradoVehiculo::fromArray((array)$bienRaw),
            (string)($row['canal_venta'] ?? 'WEB_REACT'),
            new PrimaMonetaria((float)($row['prima_mensual'] ?? ((float)$row['prima_anual'] / 12.0)), $moneda),
            isset($row['fecha_emision']) ? (string)$row['fecha_emision'] : null,
            (string)($row['created_at'] ?? gmdate('Y-m-d\TH:i:s\Z')),
            (string)($row['updated_at'] ?? gmdate('Y-m-d\TH:i:s\Z'))
        );
    }
}

