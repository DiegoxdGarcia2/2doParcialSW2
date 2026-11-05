<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Catalogo\Entities;

use AegisCore\Polizas\Domain\Catalogo\ValueObjects\TipoPlanVO;
use AegisCore\Polizas\Domain\Shared\ValueObjects\PrimaMonetaria;
use AegisCore\Polizas\Domain\Shared\ValueObjects\UuidId;

/**
 * Aggregate Root DDD del Catálogo Comercial: PlanSeguro (CU03).
 * Contiene la colección de objetos Cobertura vinculados por FK plan_id.
 */
class PlanSeguro
{
    private UuidId $id;
    private string $codigo;
    private string $nombre;
    private TipoPlanVO $tipo;
    private ?string $descripcion;
    private PrimaMonetaria $primaBaseAnual;
    private float $deducibleBasePorcentaje;
    private bool $activo;
    /** @var Cobertura[] */
    private array $coberturas;

    /**
     * @param Cobertura[] $coberturas
     */
    public function __construct(
        UuidId $id,
        string $codigo,
        string $nombre,
        TipoPlanVO $tipo,
        PrimaMonetaria $primaBaseAnual,
        float $deducibleBasePorcentaje = 10.0,
        ?string $descripcion = null,
        bool $activo = true,
        array $coberturas = []
    ) {
        $this->id = $id;
        $this->codigo = strtoupper(trim($codigo));
        $this->nombre = trim($nombre);
        $this->tipo = $tipo;
        $this->primaBaseAnual = $primaBaseAnual;
        $this->deducibleBasePorcentaje = round($deducibleBasePorcentaje, 2);
        $this->descripcion = $descripcion;
        $this->activo = $activo;
        $this->coberturas = $coberturas;
    }

    public function id(): UuidId
    {
        return $this->id;
    }

    public function codigo(): string
    {
        return $this->codigo;
    }

    public function nombre(): string
    {
        return $this->nombre;
    }

    public function tipo(): TipoPlanVO
    {
        return $this->tipo;
    }

    public function descripcion(): ?string
    {
        return $this->descripcion;
    }

    public function primaBaseAnual(): PrimaMonetaria
    {
        return $this->primaBaseAnual;
    }

    public function deducibleBasePorcentaje(): float
    {
        return $this->deducibleBasePorcentaje;
    }

    public function activo(): bool
    {
        return $this->activo;
    }

    /**
     * @return Cobertura[]
     */
    public function coberturas(): array
    {
        return $this->coberturas;
    }

    public function agregarCobertura(Cobertura $cobertura): void
    {
        $this->coberturas[] = $cobertura;
    }

    public function techoCoberturaMaximo(): float
    {
        if (empty($this->coberturas)) {
            return 25000.00;
        }
        $max = 0.0;
        foreach ($this->coberturas as $cobertura) {
            if ($cobertura->sumaAseguradaMax() > $max) {
                $max = $cobertura->sumaAseguradaMax();
            }
        }
        return $max > 0 ? $max : 25000.00;
    }

    public function toGraphQLArray(): array
    {
        return [
            'id' => $this->id->value(),
            'codigo' => $this->codigo,
            'nombre' => $this->nombre,
            'tipo' => $this->tipo->valor(),
            'descripcion' => $this->descripcion,
            'primaBaseAnual' => $this->primaBaseAnual->monto(),
            'deducibleBasePorcentaje' => $this->deducibleBasePorcentaje,
            'activo' => $this->activo,
            'coberturas' => array_map(fn(Cobertura $c) => $c->toGraphQLArray(), $this->coberturas),
        ];
    }
}

