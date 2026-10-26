package com.aegiscore.actuarial.domain.service;

import java.math.BigDecimal;
import java.math.RoundingMode;

/**
 * Servicio de Dominio Puro: CalculoActuarialService.
 * Aplica fórmulas matemáticas actuariales de deducibles, primas y márgenes de liquidación.
 */
public class CalculoActuarialService {

    private static final BigDecimal PORCENTAJE_DEDUCIBLE_DEFAULT = new BigDecimal("10.00");
    private static final BigDecimal DEDUCIBLE_MINIMO_DEFAULT = new BigDecimal("100.00");

    /**
     * Calcula el deducible aplicable en función de la suma indemnizada y las condiciones contractuales.
     */
    public BigDecimal calcularDeducible(BigDecimal montoIndemnizacion, BigDecimal porcentajeDeducible, BigDecimal deducibleMinimo) {
        if (montoIndemnizacion == null || montoIndemnizacion.compareTo(BigDecimal.ZERO) <= 0) {
            return BigDecimal.ZERO;
        }

        BigDecimal porcentaje = (porcentajeDeducible != null && porcentajeDeducible.compareTo(BigDecimal.ZERO) > 0)
                ? porcentajeDeducible
                : PORCENTAJE_DEDUCIBLE_DEFAULT;

        BigDecimal minimo = (deducibleMinimo != null && deducibleMinimo.compareTo(BigDecimal.ZERO) > 0)
                ? deducibleMinimo
                : DEDUCIBLE_MINIMO_DEFAULT;

        BigDecimal deducibleCalculado = montoIndemnizacion
                .multiply(porcentaje)
                .divide(new BigDecimal("100.00"), 2, RoundingMode.HALF_UP);

        return deducibleCalculado.max(minimo);
    }

    /**
     * Calcula el monto neto a desembolsar al cliente asegurado.
     */
    public BigDecimal calcularMontoNetoDesembolso(BigDecimal montoIndemnizacion, BigDecimal deducible) {
        if (montoIndemnizacion == null) {
            return BigDecimal.ZERO;
        }
        BigDecimal deducibleFinal = deducible != null ? deducible : BigDecimal.ZERO;
        BigDecimal neto = montoIndemnizacion.subtract(deducibleFinal);
        return neto.max(BigDecimal.ZERO).setScale(2, RoundingMode.HALF_UP);
    }

    /**
     * Valida si el ratio de solvencia técnica es aceptable después de un desembolso.
     */
    public boolean validarRatioSolvencia(BigDecimal fondoActual, BigDecimal desembolsoNeto, BigDecimal limiteMinimo) {
        if (fondoActual == null || desembolsoNeto == null || limiteMinimo == null) {
            return false;
        }
        BigDecimal fondoRemanente = fondoActual.subtract(desembolsoNeto);
        return fondoRemanente.compareTo(limiteMinimo) >= 0;
    }
}
