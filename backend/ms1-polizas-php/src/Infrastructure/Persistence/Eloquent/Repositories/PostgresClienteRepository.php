<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Infrastructure\Persistence\Eloquent\Repositories;

use AegisCore\Polizas\Domain\Cliente\Entities\Cliente;
use AegisCore\Polizas\Domain\Cliente\Repositories\ClienteRepositoryInterface;
use AegisCore\Polizas\Domain\Cliente\ValueObjects\DocumentoIdentidad;
use AegisCore\Polizas\Domain\Cliente\ValueObjects\PerfilRiesgoCliente;
use AegisCore\Polizas\Domain\Shared\ValueObjects\UuidId;
use AegisCore\Polizas\Infrastructure\Persistence\Eloquent\PdoPostgresConnection;
use Throwable;

/**
 * Repositorio de Infraestructura PostgreSQL (Eloquent/PDO): PostgresClienteRepository.
 */
class PostgresClienteRepository implements ClienteRepositoryInterface
{
    public function __construct(
        private readonly PdoPostgresConnection $connection
    ) {
    }

    public function obtenerPorId(string $id): ?Cliente
    {
        $pdo = $this->connection->getPdo();
        if ($pdo !== null) {
            try {
                $stmt = $pdo->prepare('SELECT * FROM cliente WHERE id::text = :id LIMIT 1');
                $stmt->execute(['id' => $id]);
                $row = $stmt->fetch();
                if (is_array($row)) {
                    return $this->mapRowToEntity($row);
                }
            } catch (Throwable) {
                // Fallback a estado sincronizado
            }
        }

        $state = $this->connection->readState();
        if (isset($state['clientes'][$id])) {
            return $this->mapRowToEntity($state['clientes'][$id]);
        }
        return null;
    }

    public function buscarPorDocumento(string $numeroDocumento): ?Cliente
    {
        $docNorm = strtoupper(trim($numeroDocumento));
        $pdo = $this->connection->getPdo();
        if ($pdo !== null) {
            try {
                $stmt = $pdo->prepare('SELECT * FROM cliente WHERE UPPER(numero_documento) = :doc LIMIT 1');
                $stmt->execute(['doc' => $docNorm]);
                $row = $stmt->fetch();
                if (is_array($row)) {
                    return $this->mapRowToEntity($row);
                }
            } catch (Throwable) {
                // Fallback a estado sincronizado
            }
        }

        $state = $this->connection->readState();
        foreach ($state['clientes'] as $row) {
            if (strtoupper((string)$row['numero_documento']) === $docNorm) {
                return $this->mapRowToEntity($row);
            }
        }
        return null;
    }

    public function listarTodos(): array
    {
        $pdo = $this->connection->getPdo();
        if ($pdo !== null) {
            try {
                $stmt = $pdo->query('SELECT * FROM cliente ORDER BY created_at DESC');
                $rows = $stmt->fetchAll();
                if (!empty($rows)) {
                    return array_map(fn(array $r) => $this->mapRowToEntity($r), $rows);
                }
            } catch (Throwable) {
                // Fallback
            }
        }

        $state = $this->connection->readState();
        return array_values(array_map(fn(array $r) => $this->mapRowToEntity($r), $state['clientes']));
    }

    public function guardar(Cliente $cliente): Cliente
    {
        $id = $cliente->id()->value();
        $row = [
            'id' => $id,
            'usuario_id' => $cliente->usuarioId(),
            'tipo_documento' => $cliente->documento()->tipoDocumento(),
            'numero_documento' => $cliente->documento()->numeroDocumento(),
            'nombres' => $cliente->nombres(),
            'apellidos' => $cliente->apellidos(),
            'email' => $cliente->email(),
            'telefono' => $cliente->telefono(),
            'direccion' => $cliente->direccion(),
            'ciudad' => $cliente->ciudad(),
            'score_crediticio' => $cliente->perfilRiesgo()->scoreCrediticio(),
            'perfil_riesgo' => $cliente->perfilRiesgo()->perfilRiesgo(),
            'created_at' => $cliente->createdAt(),
        ];

        $pdo = $this->connection->getPdo(true);
        if ($pdo !== null) {
            try {
                $sql = <<<SQL
                INSERT INTO cliente (
                    id, usuario_id, tipo_documento, numero_documento, nombres, apellidos,
                    email, telefono, direccion, ciudad, score_crediticio, perfil_riesgo
                ) VALUES (
                    :id, :usuario_id, :tipo_documento, :numero_documento, :nombres, :apellidos,
                    :email, :telefono, :direccion, :ciudad, :score_crediticio, :perfil_riesgo
                )
                ON CONFLICT (numero_documento) DO UPDATE SET
                    nombres = EXCLUDED.nombres,
                    apellidos = EXCLUDED.apellidos,
                    email = EXCLUDED.email,
                    telefono = EXCLUDED.telefono,
                    direccion = EXCLUDED.direccion,
                    ciudad = EXCLUDED.ciudad,
                    score_crediticio = EXCLUDED.score_crediticio,
                    perfil_riesgo = EXCLUDED.perfil_riesgo,
                    updated_at = CURRENT_TIMESTAMP
                SQL;
                $stmt = $pdo->prepare($sql);
                $stmt->execute([
                    'id' => $row['id'],
                    'usuario_id' => $row['usuario_id'],
                    'tipo_documento' => $row['tipo_documento'],
                    'numero_documento' => $row['numero_documento'],
                    'nombres' => $row['nombres'],
                    'apellidos' => $row['apellidos'],
                    'email' => $row['email'],
                    'telefono' => $row['telefono'],
                    'direccion' => $row['direccion'],
                    'ciudad' => $row['ciudad'],
                    'score_crediticio' => $row['score_crediticio'],
                    'perfil_riesgo' => $row['perfil_riesgo'],
                ]);
            } catch (Throwable) {
                // Continúa guardando en estado local sincronizado
            }
        }

        $state = $this->connection->readState();
        $state['clientes'][$id] = $row;
        $this->connection->writeState($state);

        return $cliente;
    }

    private function mapRowToEntity(array $row): Cliente
    {
        return new Cliente(
            new UuidId((string)$row['id']),
            new DocumentoIdentidad(
                (string)($row['tipo_documento'] ?? 'CI'),
                (string)($row['numero_documento'] ?? '6234891-SC')
            ),
            (string)($row['nombres'] ?? 'Carlos'),
            (string)($row['apellidos'] ?? 'Mendoza'),
            (string)($row['email'] ?? 'carlos.mendoza@gmail.com'),
            (string)($row['telefono'] ?? '+591 71099887'),
            isset($row['direccion']) ? (string)$row['direccion'] : null,
            (string)($row['ciudad'] ?? 'Santa Cruz'),
            new PerfilRiesgoCliente(
                (int)($row['score_crediticio'] ?? 780),
                isset($row['perfil_riesgo']) ? (string)$row['perfil_riesgo'] : null
            ),
            isset($row['usuario_id']) ? (string)$row['usuario_id'] : null,
            (string)($row['created_at'] ?? gmdate('Y-m-d\TH:i:s\Z'))
        );
    }
}

