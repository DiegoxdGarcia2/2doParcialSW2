package com.aegiscore.actuarial.domain.model.liquidacion;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

/**
 * Entidad de Dominio: OrdenLiquidacion (CU09).
 * Representa la instancia y estado de la transacción Saga de liquidación de indemnización.
 * Totalmente desacoplada de Spring, Hibernate y JPA (Arquitectura Hexagonal).
 */
public class OrdenLiquidacion {

    private UUID id;
    private String sagaId;
    private String reclamoIdMongo;
    private UUID polizaId;
    private UUID clienteId;
    private BigDecimal montoIndemnizacion;
    private BigDecimal deducibleAplicado;
    private BigDecimal montoNetoDesembolso;
    private EstadoSaga estadoSaga;
    private String cuentaBancariaDestino;
    private String comprobanteTransferencia;
    private String motivoCompensacion;
    private Instant fechaInicio;
    private Instant fechaFinalizacion;

    public OrdenLiquidacion() {
    }

    public OrdenLiquidacion(
            UUID id,
            String sagaId,
            String reclamoIdMongo,
            UUID polizaId,
            UUID clienteId,
            BigDecimal montoIndemnizacion,
            BigDecimal deducibleAplicado,
            BigDecimal montoNetoDesembolso,
            EstadoSaga estadoSaga,
            String cuentaBancariaDestino,
            Instant fechaInicio
    ) {
        this.id = id != null ? id : UUID.randomUUID();
        this.sagaId = sagaId;
        this.reclamoIdMongo = reclamoIdMongo;
        this.polizaId = polizaId;
        this.clienteId = clienteId;
        this.montoIndemnizacion = montoIndemnizacion;
        this.deducibleAplicado = deducibleAplicado != null ? deducibleAplicado : BigDecimal.ZERO;
        this.montoNetoDesembolso = montoNetoDesembolso;
        this.estadoSaga = estadoSaga != null ? estadoSaga : EstadoSaga.INICIADA;
        this.cuentaBancariaDestino = cuentaBancariaDestino;
        this.fechaInicio = fechaInicio != null ? fechaInicio : Instant.now();
    }

    // Reglas de negocio de transiciones de estado Saga
    public void registrarPaso1SiniestroBloqueado() {
        this.estadoSaga = EstadoSaga.PASO1_SINIESTRO_BLOQUEADO;
    }

    public void registrarPaso2CoberturaDescontada() {
        this.estadoSaga = EstadoSaga.PASO2_COBERTURA_DESCONTADA;
    }

    public void registrarPaso3DesembolsoCompletado(String comprobante) {
        this.estadoSaga = EstadoSaga.PASO3_PAGO_EMITIDO;
        this.comprobanteTransferencia = comprobante;
        this.fechaFinalizacion = Instant.now();
    }

    public void marcarCompletada() {
        this.estadoSaga = EstadoSaga.SAGA_COMPLETADA;
        if (this.fechaFinalizacion == null) {
            this.fechaFinalizacion = Instant.now();
        }
    }

    public void iniciarCompensacion(String motivo) {
        this.estadoSaga = EstadoSaga.COMPENSANDO_COBERTURA;
        this.motivoCompensacion = motivo;
    }

    public void marcarSiniestroCompensando() {
        this.estadoSaga = EstadoSaga.COMPENSANDO_SINIESTRO;
    }

    public void marcarSagaFallidaCompensada() {
        this.estadoSaga = EstadoSaga.SAGA_FALLIDA_COMPENSADA;
        this.fechaFinalizacion = Instant.now();
    }

    public boolean estaEnCompensacion() {
        return this.estadoSaga == EstadoSaga.COMPENSANDO_COBERTURA
                || this.estadoSaga == EstadoSaga.COMPENSANDO_SINIESTRO
                || this.estadoSaga == EstadoSaga.SAGA_FALLIDA_COMPENSADA;
    }

    // Getters y Setters
    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
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

    public UUID getClienteId() {
        return clienteId;
    }

    public void setClienteId(UUID clienteId) {
        this.clienteId = clienteId;
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

    public EstadoSaga getEstadoSaga() {
        return estadoSaga;
    }

    public void setEstadoSaga(EstadoSaga estadoSaga) {
        this.estadoSaga = estadoSaga;
    }

    public String getCuentaBancariaDestino() {
        return cuentaBancariaDestino;
    }

    public void setCuentaBancariaDestino(String cuentaBancariaDestino) {
        this.cuentaBancariaDestino = cuentaBancariaDestino;
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
