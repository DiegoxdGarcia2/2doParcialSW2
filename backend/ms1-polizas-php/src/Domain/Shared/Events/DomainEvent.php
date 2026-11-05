<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Shared\Events;

use DateTimeImmutable;

/**
 * Contrato base para Eventos de Dominio en DDD (MS1 PHP 8.3).
 */
abstract class DomainEvent
{
    private string $eventId;
    private DateTimeImmutable $occurredOn;

    public function __construct(?string $eventId = null, ?DateTimeImmutable $occurredOn = null)
    {
        $this->eventId = $eventId ?? self::generateUuidV4();
        $this->occurredOn = $occurredOn ?? new DateTimeImmutable('now');
    }

    public function getEventId(): string
    {
        return $this->eventId;
    }

    public function getOccurredOn(): DateTimeImmutable
    {
        return $this->occurredOn;
    }

    abstract public function getEventName(): string;

    abstract public function toPayload(): array;

    public static function generateUuidV4(): string
    {
        $data = random_bytes(16);
        $data[6] = chr((ord($data[6]) & 0x0f) | 0x40);
        $data[8] = chr((ord($data[8]) & 0x3f) | 0x80);
        return vsprintf('%s%s-%s-%s-%s-%s%s%s', str_split(bin2hex($data), 4));
    }
}

