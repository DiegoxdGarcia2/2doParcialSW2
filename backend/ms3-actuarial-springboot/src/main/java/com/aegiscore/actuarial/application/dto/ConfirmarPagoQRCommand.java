package com.aegiscore.actuarial.application.dto;

import java.math.BigDecimal;
import java.util.UUID;

public class ConfirmarPagoQRCommand {

    private UUID polizaId;
    private int numeroCuota;
    private BigDecimal monto;
    private String codigoAutorizacionBancaria;

    public ConfirmarPagoQRCommand() {
    }

    public ConfirmarPagoQRCommand(UUID polizaId, int numeroCuota, BigDecimal monto, String codigoAutorizacionBancaria) {
        this.polizaId = polizaId;
        this.numeroCuota = numeroCuota;
        this.monto = monto;
        this.codigoAutorizacionBancaria = codigoAutorizacionBancaria;
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

    public String getCodigoAutorizacionBancaria() {
        return codigoAutorizacionBancaria;
    }

    public void setCodigoAutorizacionBancaria(String codigoAutorizacionBancaria) {
        this.codigoAutorizacionBancaria = codigoAutorizacionBancaria;
    }
}
