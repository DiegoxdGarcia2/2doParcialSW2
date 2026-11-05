<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Shared\Exceptions;

use RuntimeException;

/**
 * Excepción base del Dominio (DDD) para violaciones de invariantes de negocio en MS1.
 */
class DomainException extends RuntimeException
{
    private string $errorCode;

    public function __construct(string $message, string $errorCode = 'DOMAIN_RULE_VIOLATION', int $code = 422)
    {
        parent::__construct($message, $code);
        $this->errorCode = $errorCode;
    }

    public function getErrorCode(): string
    {
        return $this->errorCode;
    }
}

