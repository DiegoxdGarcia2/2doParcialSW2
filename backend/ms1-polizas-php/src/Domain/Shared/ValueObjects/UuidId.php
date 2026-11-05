<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Shared\ValueObjects;

use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;

/**
 * Value Object DDD: Identificador único universal UUIDv4.
 */
final class UuidId
{
    private string $value;

    public function __construct(string $value)
    {
        $trimmed = trim($value);
        if ($trimmed === '') {
            throw new DomainException('El identificador UUID no puede estar vacío.', 'INVALID_UUID');
        }
        $this->value = $trimmed;
    }

    public static function generate(): self
    {
        $data = random_bytes(16);
        $data[6] = chr((ord($data[6]) & 0x0f) | 0x40);
        $data[8] = chr((ord($data[8]) & 0x3f) | 0x80);
        $uuid = vsprintf('%s%s-%s-%s-%s-%s%s%s', str_split(bin2hex($data), 4));
        return new self($uuid);
    }

    public function value(): string
    {
        return $this->value;
    }

    public function equals(self $other): bool
    {
        return strtolower($this->value) === strtolower($other->value);
    }

    public function __toString(): string
    {
        return $this->value;
    }
}

