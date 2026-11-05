<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Cliente\ValueObjects;

use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;

/**
 * Value Object DDD: DocumentoIdentidad (CI, NIT, PASAPORTE, DNI).
 */
final class DocumentoIdentidad
{
    private const TIPOS_VALIDOS = ['CI', 'NIT', 'PASAPORTE', 'DNI'];

    private string $tipoDocumento;
    private string $numeroDocumento;

    public function __construct(string $tipoDocumento, string $numeroDocumento)
    {
        $tipo = strtoupper(trim($tipoDocumento));
        if (!in_array($tipo, self::TIPOS_VALIDOS, true)) {
            $tipo = 'CI';
        }

        $numero = strtoupper(trim($numeroDocumento));
        if (strlen($numero) < 4) {
            throw new DomainException(
                'El número de documento de identidad debe tener al menos 4 caracteres.',
                'INVALID_DOCUMENT_NUMBER'
            );
        }

        $this->tipoDocumento = $tipo;
        $this->numeroDocumento = $numero;
    }

    public function tipoDocumento(): string
    {
        return $this->tipoDocumento;
    }

    public function numeroDocumento(): string
    {
        return $this->numeroDocumento;
    }
}

