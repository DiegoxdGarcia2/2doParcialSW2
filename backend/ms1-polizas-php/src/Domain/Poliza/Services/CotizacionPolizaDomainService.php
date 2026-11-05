<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Domain\Poliza\Services;

use AegisCore\Polizas\Domain\Catalogo\Entities\PlanSeguro;
use AegisCore\Polizas\Domain\Poliza\ValueObjects\BienAseguradoVehiculo;
use AegisCore\Polizas\Domain\Shared\Exceptions\DomainException;
use AegisCore\Polizas\Domain\Shared\ValueObjects\PrimaMonetaria;

/**
 * Servicio de Dominio DDD: CotizacionPolizaDomainService (CU04).
 * Calcula la prima anual y mensual ajustada por valor comercial, edad del conductor, ciudad y score crediticio.
 */
class CotizacionPolizaDomainService
{
    public function calcularCotizacion(
        PlanSeguro $plan,
        BienAseguradoVehiculo $bien,
        int $edadConductor,
        string $ciudad = 'Santa Cruz',
        int $scoreCrediticio = 780
    ): array {
        if ($edadConductor < 18 || $edadConductor > 90) {
            throw new DomainException(
                sprintf('La edad del conductor debe estar entre 18 y 90 años (recibido: %d).', $edadConductor),
                'INVALID_DRIVER_AGE'
            );
        }

        $primaBase = $plan->primaBaseAnual()->monto();
        $componenteValorBien = $bien->valorComercial() * 0.0185; // 1.85% de tasa técnica sobre valor comercial

        // Factor etario actuarial
        $factorEdad = 1.00;
        if ($edadConductor < 25) {
            $factorEdad = 1.22; // Conductores jóvenes: +22%
        } elseif ($edadConductor > 68) {
            $factorEdad = 1.12; // Mayor riesgo reflejo: +12%
        } else {
            $factorEdad = 0.96; // Tramo óptimo: -4%
        }

        // Factor antigüedad del vehículo
        $antiguedadVehiculo = max(0, (int)date('Y') - $bien->anio());
        $factorAntiguedad = 1.00 + min(0.20, $antiguedadVehiculo * 0.015);

        // Descuento por score crediticio (CU04 CotizacionResultado.descuentoScoreAplicado)
        $descuentoPorcentaje = 0.0;
        if ($scoreCrediticio >= 800) {
            $descuentoPorcentaje = 12.5;
        } elseif ($scoreCrediticio >= 720) {
            $descuentoPorcentaje = 7.5;
        } elseif ($scoreCrediticio >= 650) {
            $descuentoPorcentaje = 3.0;
        }

        $primaBruta = ($primaBase * 0.55 + $componenteValorBien) * $factorEdad * $factorAntiguedad;
        $descuentoMonto = round($primaBruta * ($descuentoPorcentaje / 100.0), 2);
        $primaAnualFinal = max(180.00, round($primaBruta - $descuentoMonto, 2));

        $primaVO = new PrimaMonetaria($primaAnualFinal, 'USD');
        $primaMensualVO = $primaVO->calcularPrimaMensual();

        return [
            'primaCalculadaAnual' => $primaVO->monto(),
            'primaCalculadaMensual' => $primaMensualVO->monto(),
            'deduciblePorcentaje' => $plan->deducibleBasePorcentaje(),
            'descuentoScoreAplicado' => $descuentoMonto,
            'validoHasta' => gmdate('Y-m-d\TH:i:s\Z', strtotime('+15 days')),
        ];
    }
}

