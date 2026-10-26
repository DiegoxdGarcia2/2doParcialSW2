package com.aegiscore.actuarial.domain;

import com.aegiscore.actuarial.domain.service.CalculoActuarialService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Pruebas Unitarias del Dominio: CalculoActuarialService (CU09)")
class CalculoActuarialServiceTest {

    private CalculoActuarialService calculoService;

    @BeforeEach
    void setUp() {
        calculoService = new CalculoActuarialService();
    }

    @Test
    @DisplayName("Debe calcular deducible aplicando 10% si supera el deducible mínimo")
    void debeCalcularDeduciblePorcentual() {
        BigDecimal indemnizacion = new BigDecimal("5000.00");
        BigDecimal porcentaje = new BigDecimal("10.00");
        BigDecimal minimo = new BigDecimal("150.00");

        BigDecimal deducible = calculoService.calcularDeducible(indemnizacion, porcentaje, minimo);

        assertEquals(new BigDecimal("500.00"), deducible);
    }

    @Test
    @DisplayName("Debe aplicar deducible mínimo si el 10% es inferior al mínimo contractual")
    void debeAplicarDeducibleMinimoSiEsMayor() {
        BigDecimal indemnizacion = new BigDecimal("800.00");
        BigDecimal porcentaje = new BigDecimal("10.00"); // 10% = 80
        BigDecimal minimo = new BigDecimal("150.00");

        BigDecimal deducible = calculoService.calcularDeducible(indemnizacion, porcentaje, minimo);

        assertEquals(new BigDecimal("150.00"), deducible);
    }

    @Test
    @DisplayName("Debe calcular monto neto de desembolso restando el deducible")
    void debeCalcularMontoNetoCorrectamente() {
        BigDecimal indemnizacion = new BigDecimal("3500.00");
        BigDecimal deducible = new BigDecimal("350.00");

        BigDecimal neto = calculoService.calcularMontoNetoDesembolso(indemnizacion, deducible);

        assertEquals(new BigDecimal("3150.00"), neto);
    }

    @Test
    @DisplayName("Debe validar que el ratio de solvencia sea suficiente")
    void debeValidarRatioSolvenciaSuficiente() {
        BigDecimal fondoReserva = new BigDecimal("500000.00");
        BigDecimal desembolso = new BigDecimal("10000.00");
        BigDecimal limiteSolvencia = new BigDecimal("100000.00");

        boolean esSolvente = calculoService.validarRatioSolvencia(fondoReserva, desembolso, limiteSolvencia);

        assertTrue(esSolvente);
    }

    @Test
    @DisplayName("Debe rechazar solvencia si el desembolso perfora el límite mínimo de reserva")
    void debeRechazarSolvenciaSiPerforaLimite() {
        BigDecimal fondoReserva = new BigDecimal("105000.00");
        BigDecimal desembolso = new BigDecimal("20000.00"); // Quedaría 85,000 < 100,000
        BigDecimal limiteSolvencia = new BigDecimal("100000.00");

        boolean esSolvente = calculoService.validarRatioSolvencia(fondoReserva, desembolso, limiteSolvencia);

        assertFalse(esSolvente);
    }
}
