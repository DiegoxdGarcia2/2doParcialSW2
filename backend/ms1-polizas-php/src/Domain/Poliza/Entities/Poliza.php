<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Poliza\Entities;

use AegisCore\Polizas\Domain\Poliza\Events\CoberturaPolizaDescontadaEvent;
use AegisCore\Polizas\Domain\Poliza\Events\CoberturaRestituidaEvent;
use AegisCore\Polizas\Domain\Poliza\Events\PolizaEmitidaEvent;
use AegisCore\Polizas\Domain\Poliza\ValueObjects\BienAseguradoVehiculo;
use AegisCore\Polizas\Domain\Poliza\ValueObjects\EstadoPolizaVO;
use AegisCore\Polizas\Domain\Shared\Events\DomainEvent;
use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;
use AegisCore\Polizas\Domain\Shared\ValueObjects\PrimaMonetaria;
use AegisCore\Polizas\Domain\Shared\ValueObjects\UuidId;
use AegisCore\Polizas\Domain\Shared\ValueObjects\VigenciaPoliza;

/**
 * AGGREGATE ROOT DDD: Poliza (Contrato de Seguro - CU02, CU03, CU04, CU05, CU09).
 * Protege los invariantes transaccionales de vigencia, prima y saldo de cobertura anual.
 */
class Poliza
{
    private UuidId $id;
    private string $numeroPoliza;
    private UuidId $clienteId;
    private UuidId $planId;
    private EstadoPolizaVO $estado;
    private ?string $fechaEmision;
    private VigenciaPoliza $vigencia;
    private PrimaMonetaria $primaAnual;
    private PrimaMonetaria $primaMensual;
    private PrimaMonetaria $saldoCoberturaRestante;
    private BienAseguradoVehiculo $bienAsegurado;
    private string $canalVenta;
    private string $createdAt;
    private string $updatedAt;

    /** @var DomainEvent[] */
    private array $domainEvents = [];

    public function __construct(
        UuidId $id,
        string $numeroPoliza,
        UuidId $clienteId,
        UuidId $planId,
        EstadoPolizaVO $estado,
        VigenciaPoliza $vigencia,
        PrimaMonetaria $primaAnual,
        PrimaMonetaria $saldoCoberturaRestante,
        BienAseguradoVehiculo $bienAsegurado,
        string $canalVenta = 'WEB_REACT',
        ?PrimaMonetaria $primaMensual = null,
        ?string $fechaEmision = null,
        ?string $createdAt = null,
        ?string $updatedAt = null
    ) {
        $this->id = $id;
        $this->numeroPoliza = strtoupper(trim($numeroPoliza));
        $this->clienteId = $clienteId;
        $this->planId = $planId;
        $this->estado = $estado;
        $this->vigencia = $vigencia;
        $this->primaAnual = $primaAnual;
        $this->primaMensual = $primaMensual ?? $primaAnual->calcularPrimaMensual();
        $this->saldoCoberturaRestante = $saldoCoberturaRestante;
        $this->bienAsegurado = $bienAsegurado;
        $this->canalVenta = in_array($canalVenta, ['WEB_REACT', 'WHATSAPP_N8N', 'OFICINA_ANGULAR', 'BROKER'], true)
            ? $canalVenta
            : 'WEB_REACT';
        $this->fechaEmision = $fechaEmision ?? gmdate('Y-m-d\TH:i:s\Z');
        $this->createdAt = $createdAt ?? gmdate('Y-m-d\TH:i:s\Z');
        $this->updatedAt = $updatedAt ?? gmdate('Y-m-d\TH:i:s\Z');
    }

    public static function emitirNueva(
        UuidId $clienteId,
        UuidId $planId,
        VigenciaPoliza $vigencia,
        PrimaMonetaria $primaAnual,
        float $techoCoberturaMaximo,
        BienAseguradoVehiculo $bienAsegurado,
        string $canalVenta = 'WEB_REACT',
        ?string $numeroPoliza = null
    ): self {
        $id = UuidId::generate();
        $codigoNumero = $numeroPoliza ?? sprintf('POL-%s-AUT-%05d', date('Y'), random_int(1000, 99999));

        $poliza = new self(
            $id,
            $codigoNumero,
            $clienteId,
            $planId,
            new EstadoPolizaVO(EstadoPolizaVO::ACTIVA),
            $vigencia,
            $primaAnual,
            new PrimaMonetaria($techoCoberturaMaximo, $primaAnual->moneda()),
            $bienAsegurado,
            $canalVenta
        );

        $poliza->recordEvent(new PolizaEmitidaEvent(
            $id->value(),
            $codigoNumero,
            $clienteId->value(),
            $primaAnual->monto(),
            $canalVenta
        ));

        return $poliza;
    }

    /**
     * Método operacional UML 2.5+ (CU09 Paso 2 de la Saga):
     * Verifica la póliza activa y descuenta el monto indemnizado del techo de cobertura anual.
     */
    public function descontarTechoAnualPoliza(
        float $montoIndemnizacion,
        string $sagaId = 'saga-local',
        string $correlationId = 'corr-local',
        string $reclamoId = 'REC-2026-00492'
    ): CoberturaPolizaDescontadaEvent {
        if (!$this->estado->permiteDescuentoCobertura()) {
            throw new DomainException(
                sprintf('La póliza %s no se encuentra activa (estado actual: %s).', $this->numeroPoliza, $this->estado->valor()),
                'POLICY_NOT_ACTIVE_FOR_SAGA'
            );
        }

        if ($montoIndemnizacion <= 0) {
            throw new DomainException('El monto de indemnización a descontar debe ser mayor a cero.', 'INVALID_INDEMNITY_AMOUNT');
        }

        $saldoPrevio = $this->saldoCoberturaRestante->monto();
        $montoDescontarVO = new PrimaMonetaria($montoIndemnizacion, $this->saldoCoberturaRestante->moneda());

        // Aplicará validación de saldo suficiente lanzando DomainException si excede
        $this->saldoCoberturaRestante = $this->saldoCoberturaRestante->descontar($montoDescontarVO);
        $this->updatedAt = gmdate('Y-m-d\TH:i:s\Z');

        $event = new CoberturaPolizaDescontadaEvent(
            $sagaId,
            $correlationId,
            $reclamoId,
            $this->id->value(),
            $montoIndemnizacion,
            $saldoPrevio,
            $this->saldoCoberturaRestante->monto()
        );
        $this->recordEvent($event);

        return $event;
    }

    /**
     * Método operacional UML 2.5+ (CU09 Compensación / Rollback de la Saga):
     * Restituye el monto descontado al saldo de cobertura anual cuando falla el Paso 3 en Spring Boot.
     */
    public function compensarCoberturaSaga(
        float $montoRestituir,
        string $sagaId = 'saga-local',
        string $correlationId = 'corr-local',
        string $reclamoId = 'REC-2026-00492',
        string $motivoFallo = 'Compensación automática por fallo en reserva técnica MS3'
    ): CoberturaRestituidaEvent {
        if ($montoRestituir <= 0) {
            throw new DomainException('El monto a restituir en compensación debe ser mayor a cero.', 'INVALID_COMPENSATION_AMOUNT');
        }

        $saldoPrevio = $this->saldoCoberturaRestante->monto();
        $montoSumarVO = new PrimaMonetaria($montoRestituir, $this->saldoCoberturaRestante->moneda());
        $this->saldoCoberturaRestante = $this->saldoCoberturaRestante->sumar($montoSumarVO);
        $this->updatedAt = gmdate('Y-m-d\TH:i:s\Z');

        $event = new CoberturaRestituidaEvent(
            $sagaId,
            $correlationId,
            $reclamoId,
            $this->id->value(),
            $montoRestituir,
            $saldoPrevio,
            $this->saldoCoberturaRestante->monto(),
            $motivoFallo
        );
        $this->recordEvent($event);

        return $event;
    }

    public function restituirSaldoCobertura(
        float $montoRestituir,
        string $sagaId = 'saga-local',
        string $correlationId = 'corr-local',
        string $reclamoId = 'REC-2026-00492',
        string $motivoFallo = 'Rollback Saga MS3'
    ): CoberturaRestituidaEvent {
        return $this->compensarCoberturaSaga($montoRestituir, $sagaId, $correlationId, $reclamoId, $motivoFallo);
    }

    public function id(): UuidId
    {
        return $this->id;
    }

    public function numeroPoliza(): string
    {
        return $this->numeroPoliza;
    }

    public function clienteId(): UuidId
    {
        return $this->clienteId;
    }

    public function planId(): UuidId
    {
        return $this->planId;
    }

    public function estado(): EstadoPolizaVO
    {
        return $this->estado;
    }

    public function fechaEmision(): ?string
    {
        return $this->fechaEmision;
    }

    public function vigencia(): VigenciaPoliza
    {
        return $this->vigencia;
    }

    public function primaAnual(): PrimaMonetaria
    {
        return $this->primaAnual;
    }

    public function primaMensual(): PrimaMonetaria
    {
        return $this->primaMensual;
    }

    public function saldoCoberturaRestante(): PrimaMonetaria
    {
        return $this->saldoCoberturaRestante;
    }

    public function bienAsegurado(): BienAseguradoVehiculo
    {
        return $this->bienAsegurado;
    }

    public function canalVenta(): string
    {
        return $this->canalVenta;
    }

    public function createdAt(): string
    {
        return $this->createdAt;
    }

    public function updatedAt(): string
    {
        return $this->updatedAt;
    }

    /**
     * @return DomainEvent[]
     */
    public function pullDomainEvents(): array
    {
        $events = $this->domainEvents;
        $this->domainEvents = [];
        return $events;
    }

    private function recordEvent(DomainEvent $event): void
    {
        $this->domainEvents[] = $event;
    }

    public function toGraphQLArray(
        ?array $clienteArray = null,
        ?array $planArray = null,
        array $facturas = [],
        array $siniestros = []
    ): array {
        return [
            'id' => $this->id->value(),
            'numeroPoliza' => $this->numeroPoliza,
            'clienteId' => $this->clienteId->value(),
            'planId' => $this->planId->value(),
            'cliente' => $clienteArray,
            'plan' => $planArray,
            'estado' => $this->estado->valor(),
            'fechaEmision' => $this->fechaEmision,
            'fechaInicio' => $this->vigencia->fechaInicioIso(),
            'fechaFin' => $this->vigencia->fechaFinIso(),
            'primaAnual' => $this->primaAnual->monto(),
            'primaMensual' => $this->primaMensual->monto(),
            'moneda' => $this->primaAnual->moneda(),
            'saldoCoberturaRestante' => $this->saldoCoberturaRestante->monto(),
            'bienAsegurado' => $this->bienAsegurado->toGraphQLArray(),
            'canalVenta' => $this->canalVenta,
            'facturas' => $facturas,
            'siniestros' => $siniestros,
            'createdAt' => $this->createdAt,
            'updatedAt' => $this->updatedAt,
        ];
    }
}

