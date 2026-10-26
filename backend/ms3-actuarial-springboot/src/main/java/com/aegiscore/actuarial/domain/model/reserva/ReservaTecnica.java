package com.aegiscore.actuarial.domain.model.reserva;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

/**
 * Entidad de Dominio: ReservaTecnica (Control Actuarial de Solvencia).
 * Gestiona el fondo matemático para liquidar siniestros sin comprometer el margen de solvencia mínimo.
 */
public class ReservaTecnica {

    private UUID id;
    private String periodo; // YYYY-MM
    private BigDecimal saldoFondoReserva;
    private BigDecimal limiteSolvenciaMinimo;
    private BigDecimal siniestrosLiquidadosAcumulado;
    private boolean alertasLiquidez;
    private Instant updatedAt;

    public ReservaTecnica() {
    }

    public ReservaTecnica(
            UUID id,
            String periodo,
            BigDecimal saldoFondoReserva,
            BigDecimal limiteSolvenciaMinimo
    ) {
        this.id = id != null ? id : UUID.randomUUID();
        this.periodo = periodo;
        this.saldoFondoReserva = saldoFondoReserva;
        this.limiteSolvenciaMinimo = limiteSolvenciaMinimo;
        this.siniestrosLiquidadosAcumulado = BigDecimal.ZERO;
        this.alertasLiquidez = false;
        this.updatedAt = Instant.now();
    }

    public boolean puedeCubrirDesembolso(BigDecimal montoNeto) {
        if (montoNeto == null || montoNeto.compareTo(BigDecimal.ZERO) <= 0) {
            return false;
        }
        BigDecimal remanente = this.saldoFondoReserva.subtract(montoNeto);
        return remanente.compareTo(this.limiteSolvenciaMinimo) >= 0;
    }

    public void descontarDesembolso(BigDecimal montoNeto) {
        this.saldoFondoReserva = this.saldoFondoReserva.subtract(montoNeto);
        this.siniestrosLiquidadosAcumulado = this.siniestrosLiquidadosAcumulado.add(montoNeto);
        this.alertasLiquidez = this.saldoFondoReserva.compareTo(this.limiteSolvenciaMinimo.multiply(BigDecimal.valueOf(1.1))) <= 0;
        this.updatedAt = Instant.now();
    }

    public void restituirDesembolso(BigDecimal montoNeto) {
        this.saldoFondoReserva = this.saldoFondoReserva.add(montoNeto);
        this.siniestrosLiquidadosAcumulado = this.siniestrosLiquidadosAcumulado.subtract(montoNeto);
        this.updatedAt = Instant.now();
    }

    // Getters y Setters
    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public String getPeriodo() {
        return periodo;
    }

    public void setPeriodo(String periodo) {
        this.periodo = periodo;
    }

    public BigDecimal getSaldoFondoReserva() {
        return saldoFondoReserva;
    }

    public void setSaldoFondoReserva(BigDecimal saldoFondoReserva) {
        this.saldoFondoReserva = saldoFondoReserva;
    }

    public BigDecimal getLimiteSolvenciaMinimo() {
        return limiteSolvenciaMinimo;
    }

    public void setLimiteSolvenciaMinimo(BigDecimal limiteSolvenciaMinimo) {
        this.limiteSolvenciaMinimo = limiteSolvenciaMinimo;
    }

    public BigDecimal getSiniestrosLiquidadosAcumulado() {
        return siniestrosLiquidadosAcumulado;
    }

    public void setSiniestrosLiquidadosAcumulado(BigDecimal siniestrosLiquidadosAcumulado) {
        this.siniestrosLiquidadosAcumulado = siniestrosLiquidadosAcumulado;
    }

    public boolean isAlertasLiquidez() {
        return alertasLiquidez;
    }

    public void setAlertasLiquidez(boolean alertasLiquidez) {
        this.alertasLiquidez = alertasLiquidez;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(Instant updatedAt) {
        this.updatedAt = updatedAt;
    }
}
