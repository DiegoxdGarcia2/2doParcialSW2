<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Catalogo\Entities;

use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;
use AegisCore\Polizas\Domain\Shared\ValueObjects\UuidId;

/**
 * Entidad de Dominio DDD: Cobertura (Asociada con Clave Foránea FK a PlanSeguro - CU03).
 */
class Cobertura
{
    private UuidId $id;
    private UuidId $planId;
    private string $codigo;
    private string $nombre;
    private ?string $descripcion;
    private float $sumaAseguradaMax;
    private float $deducibleMinimo;
    private float $deduciblePorcentaje;
    private bool $obligatoria;

    public function __construct(
        UuidId $id,
        UuidId $planId,
        string $codigo,
        string $nombre,
        float $sumaAseguradaMax,
        float $deducibleMinimo = 100.0,
        float $deduciblePorcentaje = 10.0,
        ?string $descripcion = null,
        bool $obligatoria = true
    ) {
        if ($sumaAseguradaMax <= 0) {
            throw new DomainException('La suma asegurada máxima debe ser mayor a cero.', 'INVALID_COVERAGE_MAX');
        }
        $this->id = $id;
        $this->planId = $planId;
        $this->codigo = strtoupper(trim($codigo));
        $this->nombre = trim($nombre);
        $this->descripcion = $descripcion;
        $this->sumaAseguradaMax = round($sumaAseguradaMax, 2);
        $this->deducibleMinimo = round($deducibleMinimo, 2);
        $this->deduciblePorcentaje = round($deduciblePorcentaje, 2);
        $this->obligatoria = $obligatoria;
    }

    public function id(): UuidId
    {
        return $this->id;
    }

    public function planId(): UuidId
    {
        return $this->planId;
    }

    public function codigo(): string
    {
        return $this->codigo;
    }

    public function nombre(): string
    {
        return $this->nombre;
    }

    public function descripcion(): ?string
    {
        return $this->descripcion;
    }

    public function sumaAseguradaMax(): float
    {
        return $this->sumaAseguradaMax;
    }

    public function deducibleMinimo(): float
    {
        return $this->deducibleMinimo;
    }

    public function deduciblePorcentaje(): float
    {
        return $this->deduciblePorcentaje;
    }

    public function obligatoria(): bool
    {
        return $this->obligatoria;
    }

    public function toGraphQLArray(): array
    {
        return [
            'id' => $this->id->value(),
            'planId' => $this->planId->value(),
            'codigo' => $this->codigo,
            'nombre' => $this->nombre,
            'descripcion' => $this->descripcion,
            'sumaAseguradaMax' => $this->sumaAseguradaMax,
            'deducibleMinimo' => $this->deducibleMinimo,
            'deduciblePorcentaje' => $this->deduciblePorcentaje,
            'obligatoria' => $this->obligatoria,
        ];
    }
}

