package com.aegiscore.actuarial.application.dto;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

public class PagoQRResponseDTO {

    private UUID pagoId;
    private UUID polizaId;
    private int numeroCuota;
    private BigDecimal monto;
    private String moneda;
    private String metodoPago;
    private String idempotencyKey;
    private String qrImagenPayload;
    private String codigoAutorizacionBancaria;
    private String estado;
    private Instant fechaPago;
    private String mensaje;

    public PagoQRResponseDTO() {
    }

    public UUID getPagoId() {
        return pagoId;
    }

    public void setPagoId(UUID pagoId) {
        this.pagoId = pagoId;
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

    public String getMetodoPago() {
        return metodoPago;
    }

    public void setMetodoPago(String metodoPago) {
        this.metodoPago = metodoPago;
    }

    public String getIdempotencyKey() {
        return idempotencyKey;
    }

    public void setIdempotencyKey(String idempotencyKey) {
        this.idempotencyKey = idempotencyKey;
    }

    public String getQrImagenPayload() {
        return qrImagenPayload;
    }

    public void setQrImagenPayload(String qrImagenPayload) {
        this.qrImagenPayload = qrImagenPayload;
    }

    public String getCodigoAutorizacionBancaria() {
        return codigoAutorizacionBancaria;
    }

    public void setCodigoAutorizacionBancaria(String codigoAutorizacionBancaria) {
        this.codigoAutorizacionBancaria = codigoAutorizacionBancaria;
    }

    public String getEstado() {
        return estado;
    }

    public void setEstado(String estado) {
        this.estado = estado;
    }

    public Instant getFechaPago() {
        return fechaPago;
    }

    public void setFechaPago(Instant fechaPago) {
        this.fechaPago = fechaPago;
    }

    public String getMensaje() {
        return mensaje;
    }

    public void setMensaje(String mensaje) {
        this.mensaje = mensaje;
    }
}
