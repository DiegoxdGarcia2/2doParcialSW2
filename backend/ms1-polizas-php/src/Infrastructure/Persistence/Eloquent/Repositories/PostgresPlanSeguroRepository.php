<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Infrastructure\Persistence\Eloquent\Repositories;

use AegisCore\Polizas\Domain\Catalogo\Entities\Cobertura;
use AegisCore\Polizas\Domain\Catalogo\Entities\PlanSeguro;
use AegisCore\Polizas\Domain\Catalogo\Repositories\PlanSeguroRepositoryInterface;
use AegisCore\Polizas\Domain\Catalogo\ValueObjects\TipoPlanVO;
use AegisCore\Polizas\Domain\Shared\ValueObjects\PrimaMonetaria;
use AegisCore\Polizas\Domain\Shared\ValueObjects\UuidId;
use AegisCore\Polizas\Infrastructure\Persistence\Eloquent\PdoPostgresConnection;
use Throwable;

/**
 * Repositorio de Infraestructura PostgreSQL (Eloquent/PDO): PostgresPlanSeguroRepository.
 * Gestiona el catálogo de planes y sus coberturas vinculadas mediante Clave Foránea (plan_id).
 */
class PostgresPlanSeguroRepository implements PlanSeguroRepositoryInterface
{
    public function __construct(
        private readonly PdoPostgresConnection $connection
    ) {
    }

    public function listarPlanes(?string $tipo = null): array
    {
        $pdo = $this->connection->getPdo();
        if ($pdo !== null) {
            try {
                if ($tipo !== null && trim($tipo) !== '') {
                    $stmt = $pdo->prepare('SELECT * FROM plan_seguro WHERE tipo = :tipo ORDER BY codigo ASC');
                    $stmt->execute(['tipo' => strtoupper(trim($tipo))]);
                } else {
                    $stmt = $pdo->query('SELECT * FROM plan_seguro ORDER BY codigo ASC');
                }
                $planRows = $stmt->fetchAll();
                if (!empty($planRows)) {
                    $result = [];
                    foreach ($planRows as $pRow) {
                        $cobStmt = $pdo->prepare('SELECT * FROM cobertura WHERE plan_id = :pid ORDER BY codigo ASC');
                        $cobStmt->execute(['pid' => $pRow['id']]);
                        $pRow['coberturas'] = $cobStmt->fetchAll() ?: [];
                        $result[] = $this->mapRowToEntity($pRow);
                    }
                    return $result;
                }
            } catch (Throwable) {
                // Fallback a estado local
            }
        }

        $state = $this->connection->readState();
        $planes = [];
        foreach ($state['planes'] as $row) {
            if ($tipo !== null && trim($tipo) !== '' && strtoupper((string)$row['tipo']) !== strtoupper(trim($tipo))) {
                continue;
            }
            $planes[] = $this->mapRowToEntity($row);
        }
        return $planes;
    }

    public function obtenerPorId(string $id): ?PlanSeguro
    {
        $pdo = $this->connection->getPdo();
        if ($pdo !== null) {
            try {
                $stmt = $pdo->prepare('SELECT * FROM plan_seguro WHERE id::text = :id LIMIT 1');
                $stmt->execute(['id' => $id]);
                $pRow = $stmt->fetch();
                if (is_array($pRow)) {
                    $cobStmt = $pdo->prepare('SELECT * FROM cobertura WHERE plan_id = :pid ORDER BY codigo ASC');
                    $cobStmt->execute(['pid' => $pRow['id']]);
                    $pRow['coberturas'] = $cobStmt->fetchAll() ?: [];
                    return $this->mapRowToEntity($pRow);
                }
            } catch (Throwable) {
                // Fallback
            }
        }

        $state = $this->connection->readState();
        if (isset($state['planes'][$id])) {
            return $this->mapRowToEntity($state['planes'][$id]);
        }
        return null;
    }

    public function obtenerPorCodigo(string $codigo): ?PlanSeguro
    {
        $codeNorm = strtoupper(trim($codigo));
        $pdo = $this->connection->getPdo();
        if ($pdo !== null) {
            try {
                $stmt = $pdo->prepare('SELECT * FROM plan_seguro WHERE UPPER(codigo) = :cod LIMIT 1');
                $stmt->execute(['cod' => $codeNorm]);
                $pRow = $stmt->fetch();
                if (is_array($pRow)) {
                    $cobStmt = $pdo->prepare('SELECT * FROM cobertura WHERE plan_id = :pid ORDER BY codigo ASC');
                    $cobStmt->execute(['pid' => $pRow['id']]);
                    $pRow['coberturas'] = $cobStmt->fetchAll() ?: [];
                    return $this->mapRowToEntity($pRow);
                }
            } catch (Throwable) {
                // Fallback
            }
        }

        $state = $this->connection->readState();
        foreach ($state['planes'] as $row) {
            if (strtoupper((string)$row['codigo']) === $codeNorm) {
                return $this->mapRowToEntity($row);
            }
        }
        return null;
    }

    public function guardarPlan(PlanSeguro $plan): PlanSeguro
    {
        $id = $plan->id()->value();
        $coberturasRows = [];
        foreach ($plan->coberturas() as $cob) {
            $coberturasRows[] = [
                'id' => $cob->id()->value(),
                'plan_id' => $id,
                'codigo' => $cob->codigo(),
                'nombre' => $cob->nombre(),
                'descripcion' => $cob->descripcion(),
                'suma_asegurada_max' => $cob->sumaAseguradaMax(),
                'deducible_minimo' => $cob->deducibleMinimo(),
                'deducible_porcentaje' => $cob->deduciblePorcentaje(),
                'obligatoria' => $cob->obligatoria(),
            ];
        }

        $row = [
            'id' => $id,
            'codigo' => $plan->codigo(),
            'nombre' => $plan->nombre(),
            'tipo' => $plan->tipo()->valor(),
            'descripcion' => $plan->descripcion(),
            'prima_base_anual' => $plan->primaBaseAnual()->monto(),
            'deducible_base_porcentaje' => $plan->deducibleBasePorcentaje(),
            'activo' => $plan->activo(),
            'coberturas' => $coberturasRows,
        ];

        $pdo = $this->connection->getPdo(true);
        if ($pdo !== null) {
            try {
                $sql = <<<SQL
                INSERT INTO plan_seguro (
                    id, codigo, nombre, tipo, descripcion, prima_base_anual, deducible_base_porcentaje, activo
                ) VALUES (
                    :id, :codigo, :nombre, :tipo, :descripcion, :prima_base_anual, :deducible_base_porcentaje, :activo
                )
                ON CONFLICT (codigo) DO UPDATE SET
                    nombre = EXCLUDED.nombre,
                    descripcion = EXCLUDED.descripcion,
                    prima_base_anual = EXCLUDED.prima_base_anual,
                    deducible_base_porcentaje = EXCLUDED.deducible_base_porcentaje,
                    activo = EXCLUDED.activo,
                    updated_at = CURRENT_TIMESTAMP
                SQL;
                $stmt = $pdo->prepare($sql);
                $stmt->execute([
                    'id' => $row['id'],
                    'codigo' => $row['codigo'],
                    'nombre' => $row['nombre'],
                    'tipo' => $row['tipo'],
                    'descripcion' => $row['descripcion'],
                    'prima_base_anual' => $row['prima_base_anual'],
                    'deducible_base_porcentaje' => $row['deducible_base_porcentaje'],
                    'activo' => $row['activo'] ? 'true' : 'false',
                ]);

                foreach ($plan->coberturas() as $cob) {
                    $this->guardarCoberturaEnPdo($pdo, $cob);
                }
            } catch (Throwable) {
                // Continúa en estado local
            }
        }

        $state = $this->connection->readState();
        $state['planes'][$id] = $row;
        $this->connection->writeState($state);

        return $plan;
    }

    public function guardarCobertura(Cobertura $cobertura): Cobertura
    {
        $pdo = $this->connection->getPdo(true);
        if ($pdo !== null) {
            try {
                $this->guardarCoberturaEnPdo($pdo, $cobertura);
            } catch (Throwable) {
                // Continúa
            }
        }

        $state = $this->connection->readState();
        $planId = $cobertura->planId()->value();
        if (isset($state['planes'][$planId])) {
            $state['planes'][$planId]['coberturas'][] = [
                'id' => $cobertura->id()->value(),
                'plan_id' => $planId,
                'codigo' => $cobertura->codigo(),
                'nombre' => $cobertura->nombre(),
                'descripcion' => $cobertura->descripcion(),
                'suma_asegurada_max' => $cobertura->sumaAseguradaMax(),
                'deducible_minimo' => $cobertura->deducibleMinimo(),
                'deducible_porcentaje' => $cobertura->deduciblePorcentaje(),
                'obligatoria' => $cobertura->obligatoria(),
            ];
            $this->connection->writeState($state);
        }

        return $cobertura;
    }

    private function guardarCoberturaEnPdo(\PDO $pdo, Cobertura $cob): void
    {
        $sql = <<<SQL
        INSERT INTO cobertura (
            id, plan_id, codigo, nombre, descripcion, suma_asegurada_max, deducible_minimo, deducible_porcentaje, obligatoria
        ) VALUES (
            :id, :plan_id, :codigo, :nombre, :descripcion, :suma_asegurada_max, :deducible_minimo, :deducible_porcentaje, :obligatoria
        )
        ON CONFLICT (plan_id, codigo) DO UPDATE SET
            nombre = EXCLUDED.nombre,
            descripcion = EXCLUDED.descripcion,
            suma_asegurada_max = EXCLUDED.suma_asegurada_max,
            deducible_minimo = EXCLUDED.deducible_minimo,
            deducible_porcentaje = EXCLUDED.deducible_porcentaje
        SQL;
        $stmt = $pdo->prepare($sql);
        $stmt->execute([
            'id' => $cob->id()->value(),
            'plan_id' => $cob->planId()->value(),
            'codigo' => $cob->codigo(),
            'nombre' => $cob->nombre(),
            'descripcion' => $cob->descripcion(),
            'suma_asegurada_max' => $cob->sumaAseguradaMax(),
            'deducible_minimo' => $cob->deducibleMinimo(),
            'deducible_porcentaje' => $cob->deduciblePorcentaje(),
            'obligatoria' => $cob->obligatoria() ? 'true' : 'false',
        ]);
    }

    private function mapRowToEntity(array $row): PlanSeguro
    {
        $planId = new UuidId((string)$row['id']);
        $coberturas = [];
        foreach ((array)($row['coberturas'] ?? []) as $cRow) {
            $coberturas[] = new Cobertura(
                new UuidId((string)$cRow['id']),
                $planId,
                (string)$cRow['codigo'],
                (string)$cRow['nombre'],
                (float)$cRow['suma_asegurada_max'],
                (float)($cRow['deducible_minimo'] ?? 100.0),
                (float)($cRow['deducible_porcentaje'] ?? 10.0),
                isset($cRow['descripcion']) ? (string)$cRow['descripcion'] : null,
                (bool)($cRow['obligatoria'] ?? true)
            );
        }

        return new PlanSeguro(
            $planId,
            (string)$row['codigo'],
            (string)$row['nombre'],
            new TipoPlanVO((string)$row['tipo']),
            new PrimaMonetaria((float)$row['prima_base_anual'], 'USD'),
            (float)($row['deducible_base_porcentaje'] ?? 10.0),
            isset($row['descripcion']) ? (string)$row['descripcion'] : null,
            (bool)($row['activo'] ?? true),
            $coberturas
        );
    }
}

