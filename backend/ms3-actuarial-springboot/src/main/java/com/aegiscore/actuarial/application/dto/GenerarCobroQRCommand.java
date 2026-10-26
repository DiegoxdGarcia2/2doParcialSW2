package com.aegiscore.actuarial.application.dto;

import java.math.BigDecimal;
import java.util.UUID;

public class GenerarCobroQRCommand {

    private UUID polizaId;
    private int numeroCuota;
    private BigDecimal monto;
    private String moneda;

    public GenerarCobroQRCommand() {
    }

    public GenerarCobroQRCommand(UUID polizaId, int numeroCuota, BigDecimal monto, String moneda) {
        this.polizaId = polizaId;
        this.numeroCuota = numeroCuota;
        this.monto = monto;
        this.moneda = moneda != null ? moneda : "USD";
    }

    public UUID getPolizaId() {
        return polizaId;
    }

    public void setPolizaId(UUID polizaId) {
        this.polizaId = polizaId;
    }

    public int getNumeroCuota() {
        return numeroCuota;
    }

    public void setNumeroCuota(int numeroCuota) {
        this.numeroCuota = numeroCuota;
    }

    public BigDecimal getMonto() {
        return monto;
    }

    public void setMonto(BigDecimal monto) {
        this.monto = monto;
    }

    public String getMoneda() {
        return moneda;
    }

    public void setMoneda(String moneda) {
        this.moneda = moneda;
    }
}
