package com.aegiscore.actuarial.application.dto;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

public class LiquidacionSagaResponseDTO {

    private String sagaId;
    private String reclamoIdMongo;
    private UUID polizaId;
    private BigDecimal montoIndemnizacion;
    private BigDecimal deducibleAplicado;
    private BigDecimal montoNetoDesembolso;
    private String estadoSaga;
    private String comprobanteTransferencia;
    private String motivoCompensacion;
    private String mensaje;
    private Instant fechaInicio;
    private Instant fechaFinalizacion;

    public LiquidacionSagaResponseDTO() {
    }

    public String getSagaId() {
        return sagaId;
    }

    public void setSagaId(String sagaId) {
        this.sagaId = sagaId;
    }

    public String getReclamoIdMongo() {
        return reclamoIdMongo;
    }

    public void setReclamoIdMongo(String reclamoIdMongo) {
        this.reclamoIdMongo = reclamoIdMongo;
    }

    public UUID getPolizaId() {
        return polizaId;
    }

    public void setPolizaId(UUID polizaId) {
        this.polizaId = polizaId;
    }

    public BigDecimal getMontoIndemnizacion() {
        return montoIndemnizacion;
    }

    public void setMontoIndemnizacion(BigDecimal montoIndemnizacion) {
        this.montoIndemnizacion = montoIndemnizacion;
    }

    public BigDecimal getDeducibleAplicado() {
        return deducibleAplicado;
    }

    public void setDeducibleAplicado(BigDecimal deducibleAplicado) {
        this.deducibleAplicado = deducibleAplicado;
    }

    public BigDecimal getMontoNetoDesembolso() {
        return montoNetoDesembolso;
    }

    public void setMontoNetoDesembolso(BigDecimal montoNetoDesembolso) {
        this.montoNetoDesembolso = montoNetoDesembolso;
    }

    public String getEstadoSaga() {
        return estadoSaga;
    }

    public void setEstadoSaga(String estadoSaga) {
        this.estadoSaga = estadoSaga;
    }

    public String getComprobanteTransferencia() {
        return comprobanteTransferencia;
    }

    public void setComprobanteTransferencia(String comprobanteTransferencia) {
        this.comprobanteTransferencia = comprobanteTransferencia;
    }

    public String getMotivoCompensacion() {
        return motivoCompensacion;
    }

    public void setMotivoCompensacion(String motivoCompensacion) {
        this.motivoCompensacion = motivoCompensacion;
    }

    public String getMensaje() {
        return mensaje;
    }

    public void setMensaje(String mensaje) {
        this.mensaje = mensaje;
    }

    public Instant getFechaInicio() {
        return fechaInicio;
    }

    public void setFechaInicio(Instant fechaInicio) {
        this.fechaInicio = fechaInicio;
    }

    public Instant getFechaFinalizacion() {
        return fechaFinalizacion;
    }

    public void setFechaFinalizacion(Instant fechaFinalizacion) {
        this.fechaFinalizacion = fechaFinalizacion;
    }
}
