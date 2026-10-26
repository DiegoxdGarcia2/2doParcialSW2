package com.aegiscore.actuarial.domain.model.cobranza;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

/**
 * Entidad de Dominio: PagoPrima (CU10).
 * Modela el pago recurrente de primas mediante QR con control estricto de Idempotencia.
 */
public class PagoPrima {

    private UUID id;
    private UUID polizaId;
    private int numeroCuota;
    private BigDecimal monto;
    private String moneda;
    private MetodoPago metodoPago;
    private String idempotencyKey; // UUIDv4
    private String qrImagenPayload;
    private String codigoAutorizacionBancaria;
    private EstadoPago estado;
    private Instant fechaPago;
    private Instant createdAt;

    public PagoPrima() {
    }

    public PagoPrima(
            UUID id,
            UUID polizaId,
            int numeroCuota,
            BigDecimal monto,
            String moneda,
            MetodoPago metodoPago,
            String idempotencyKey,
            String qrImagenPayload
    ) {
        this.id = id != null ? id : UUID.randomUUID();
        this.polizaId = polizaId;
        this.numeroCuota = numeroCuota;
        this.monto = monto;
        this.moneda = moneda != null ? moneda : "USD";
        this.metodoPago = metodoPago != null ? metodoPago : MetodoPago.QR_SIMPLE;
        this.idempotencyKey = idempotencyKey;
        this.qrImagenPayload = qrImagenPayload;
        this.estado = EstadoPago.PENDIENTE;
        this.createdAt = Instant.now();
    }

    public void confirmarPagoExitoso(String codigoAutorizacion) {
        this.estado = EstadoPago.EXITOSO;
        this.codigoAutorizacionBancaria = codigoAutorizacion;
        this.fechaPago = Instant.now();
    }

    public void marcarFallido() {
        this.estado = EstadoPago.FALLIDO;
    }

    // Getters y Setters
    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
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

    public MetodoPago getMetodoPago() {
        return metodoPago;
    }

    public void setMetodoPago(MetodoPago metodoPago) {
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

    public EstadoPago getEstado() {
        return estado;
    }

    public void setEstado(EstadoPago estado) {
        this.estado = estado;
    }

    public Instant getFechaPago() {
        return fechaPago;
    }

    public void setFechaPago(Instant fechaPago) {
        this.fechaPago = fechaPago;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }
}
