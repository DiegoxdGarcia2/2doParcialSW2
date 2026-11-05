<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Cliente\Entities;

use AegisCore\Polizas\Domain\Cliente\ValueObjects\DocumentoIdentidad;
use AegisCore\Polizas\Domain\Cliente\ValueObjects\PerfilRiesgoCliente;
use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;
use AegisCore\Polizas\Domain\Shared\ValueObjects\UuidId;

/**
 * Entidad de Dominio DDD: Cliente (Asegurado / Tomador de Póliza - CU02, CU03, CU04).
 */
class Cliente
{
    private UuidId $id;
    private ?string $usuarioId;
    private DocumentoIdentidad $documento;
    private string $nombres;
    private string $apellidos;
    private string $email;
    private string $telefono;
    private ?string $direccion;
    private string $ciudad;
    private PerfilRiesgoCliente $perfilRiesgo;
    private string $createdAt;

    public function __construct(
        UuidId $id,
        DocumentoIdentidad $documento,
        string $nombres,
        string $apellidos,
        string $email,
        string $telefono,
        ?string $direccion = null,
        string $ciudad = 'Santa Cruz',
        ?PerfilRiesgoCliente $perfilRiesgo = null,
        ?string $usuarioId = null,
        ?string $createdAt = null
    ) {
        $nombresTrim = trim($nombres);
        $apellidosTrim = trim($apellidos);
        if ($nombresTrim === '' || $apellidosTrim === '') {
            throw new DomainException('Los nombres y apellidos del cliente son obligatorios.', 'INVALID_CLIENT_NAME');
        }

        $this->id = $id;
        $this->usuarioId = $usuarioId;
        $this->documento = $documento;
        $this->nombres = $nombresTrim;
        $this->apellidos = $apellidosTrim;
        $this->email = strtolower(trim($email));
        $this->telefono = trim($telefono);
        $this->direccion = $direccion;
        $this->ciudad = trim($ciudad) !== '' ? trim($ciudad) : 'Santa Cruz';
        $this->perfilRiesgo = $perfilRiesgo ?? new PerfilRiesgoCliente(750, 'MODERADO');
        $this->createdAt = $createdAt ?? gmdate('Y-m-d\TH:i:s\Z');
    }

    public function id(): UuidId
    {
        return $this->id;
    }

    public function usuarioId(): ?string
    {
        return $this->usuarioId;
    }

    public function documento(): DocumentoIdentidad
    {
        return $this->documento;
    }

    public function nombres(): string
    {
        return $this->nombres;
    }

    public function apellidos(): string
    {
        return $this->apellidos;
    }

    public function nombreCompleto(): string
    {
        return trim($this->nombres . ' ' . $this->apellidos);
    }

    public function email(): string
    {
        return $this->email;
    }

    public function telefono(): string
    {
        return $this->telefono;
    }

    public function direccion(): ?string
    {
        return $this->direccion;
    }

    public function ciudad(): string
    {
        return $this->ciudad;
    }

    public function perfilRiesgo(): PerfilRiesgoCliente
    {
        return $this->perfilRiesgo;
    }

    public function createdAt(): string
    {
        return $this->createdAt;
    }

    public function toGraphQLArray(array $polizas = []): array
    {
        return [
            'id' => $this->id->value(),
            'usuarioId' => $this->usuarioId,
            'tipoDocumento' => $this->documento->tipoDocumento(),
            'numeroDocumento' => $this->documento->numeroDocumento(),
            'nombres' => $this->nombres,
            'apellidos' => $this->apellidos,
            'nombreCompleto' => $this->nombreCompleto(),
            'email' => $this->email,
            'telefono' => $this->telefono,
            'direccion' => $this->direccion,
            'ciudad' => $this->ciudad,
            'scoreCrediticio' => $this->perfilRiesgo->scoreCrediticio(),
            'perfilRiesgo' => $this->perfilRiesgo->perfilRiesgo(),
            'polizas' => $polizas,
            'createdAt' => $this->createdAt,
        ];
    }
}

