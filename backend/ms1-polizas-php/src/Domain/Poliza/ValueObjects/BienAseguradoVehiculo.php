<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Poliza\ValueObjects;

use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;

/**
 * Value Object DDD: BienAseguradoVehiculo (Almacenado como JSONB en PostgreSQL poliza.datos_bien_asegurado).
 */
final class BienAseguradoVehiculo
{
    private string $placa;
    private string $vin;
    private string $marca;
    private string $modelo;
    private int $anio;
    private string $color;
    private float $valorComercial;

    public function __construct(
        string $placa,
        string $vin,
        string $marca,
        string $modelo,
        int $anio,
        float $valorComercial,
        ?string $color = 'Blanco Perlado'
    ) {
        $placaClean = strtoupper(trim($placa));
        if ($placaClean === '') {
            throw new DomainException('La placa del vehículo asegurado es obligatoria.', 'INVALID_VEHICLE_PLATE');
        }
        if ($valorComercial <= 0) {
            throw new DomainException('El valor comercial del vehículo debe ser mayor a cero.', 'INVALID_VEHICLE_VALUE');
        }
        if ($anio < 1980 || $anio > (int)date('Y') + 2) {
            throw new DomainException(
                sprintf('Año de fabricación del vehículo fuera de rango permitido: %d.', $anio),
                'INVALID_VEHICLE_YEAR'
            );
        }

        $this->placa = $placaClean;
        $this->vin = strtoupper(trim($vin)) !== '' ? strtoupper(trim($vin)) : 'VIN-' . substr(md5($placaClean), 0, 12);
        $this->marca = trim($marca) !== '' ? trim($marca) : 'Toyota';
        $this->modelo = trim($modelo) !== '' ? trim($modelo) : 'Hilux 4x4';
        $this->anio = $anio;
        $this->color = ($color !== null && trim($color) !== '') ? trim($color) : 'Blanco Perlado';
        $this->valorComercial = round($valorComercial, 2);
    }

    public static function fromArray(array $data): self
    {
        return new self(
            (string)($data['placa'] ?? '4028-PLK'),
            (string)($data['vin'] ?? '8AJBA3CD701982736'),
            (string)($data['marca'] ?? 'Toyota'),
            (string)($data['modelo'] ?? 'Hilux 4x4'),
            (int)($data['anio'] ?? 2023),
            (float)($data['valorComercial'] ?? $data['valor_comercial'] ?? 25000.00),
            (string)($data['color'] ?? 'Blanco Perlado')
        );
    }

    public function placa(): string
    {
        return $this->placa;
    }

    public function vin(): string
    {
        return $this->vin;
    }

    public function marca(): string
    {
        return $this->marca;
    }

    public function modelo(): string
    {
        return $this->modelo;
    }

    public function anio(): int
    {
        return $this->anio;
    }

    public function color(): string
    {
        return $this->color;
    }

    public function valorComercial(): float
    {
        return $this->valorComercial;
    }

    public function toDatabaseJson(): array
    {
        return [
            'placa' => $this->placa,
            'vin' => $this->vin,
            'marca' => $this->marca,
            'modelo' => $this->modelo,
            'anio' => $this->anio,
            'color' => $this->color,
            'valor_comercial' => $this->valorComercial,
        ];
    }

    public function toGraphQLArray(): array
    {
        return [
            'placa' => $this->placa,
            'vin' => $this->vin,
            'marca' => $this->marca,
            'modelo' => $this->modelo,
            'anio' => $this->anio,
            'color' => $this->color,
            'valorComercial' => $this->valorComercial,
        ];
    }
}

