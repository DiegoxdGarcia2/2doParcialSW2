package com.aegiscore.actuarial.application.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

/**
 * DTO que representa el contrato inmutable de eventos Saga en Kafka.
 * Refleja exactamente contracts/saga-events.schema.json.
 */
public class SagaEventDTO {

    @JsonProperty("saga_id")
    private String sagaId;

    @JsonProperty("correlation_id")
    private String correlationId;

    @JsonProperty("event_type")
    private String eventType;

    @JsonProperty("timestamp")
    private String timestamp;

    @JsonProperty("source_service")
    private String sourceService;

    @JsonProperty("target_topic")
    private String targetTopic;

    @JsonProperty("payload")
    private Payload payload;

    public SagaEventDTO() {
    }

    public SagaEventDTO(String sagaId, String correlationId, String eventType, String targetTopic, Payload payload) {
        this.sagaId = sagaId;
        this.correlationId = correlationId != null ? correlationId : UUID.randomUUID().toString();
        this.eventType = eventType;
        this.timestamp = Instant.now().toString();
        this.sourceService = "ms3-actuarial-springboot";
        this.targetTopic = targetTopic;
        this.payload = payload;
    }

    public static class Payload {
        @JsonProperty("reclamo_id")
        private String reclamoId;

        @JsonProperty("poliza_id")
        private String polizaId;

        @JsonProperty("cliente_id")
        private String clienteId;

        @JsonProperty("monto_indemnizacion")
        private BigDecimal montoIndemnizacion;

        @JsonProperty("deducible_aplicado")
        private BigDecimal deducibleAplicado;

        @JsonProperty("monto_neto_desembolso")
        private BigDecimal montoNetoDesembolso;

        @JsonProperty("cuenta_bancaria_destino")
        private String cuentaBancariaDestino;

        @JsonProperty("motivo_rechazo")
        private String motivoRechazo;

        @JsonProperty("comprobante_id")
        private String comprobanteId;

        public Payload() {
        }

        public String getReclamoId() {
            return reclamoId;
        }

        public void setReclamoId(String reclamoId) {
            this.reclamoId = reclamoId;
        }

        public String getPolizaId() {
            return polizaId;
        }

        public void setPolizaId(String polizaId) {
            this.polizaId = polizaId;
        }

        public String getClienteId() {
            return clienteId;
        }

        public void setClienteId(String clienteId) {
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

        public String getCuentaBancariaDestino() {
            return cuentaBancariaDestino;
        }

        public void setCuentaBancariaDestino(String cuentaBancariaDestino) {
            this.cuentaBancariaDestino = cuentaBancariaDestino;
        }

        public String getMotivoRechazo() {
            return motivoRechazo;
        }

        public void setMotivoRechazo(String motivoRechazo) {
            this.motivoRechazo = motivoRechazo;
        }

        public String getComprobanteId() {
            return comprobanteId;
        }

        public void setComprobanteId(String comprobanteId) {
            this.comprobanteId = comprobanteId;
        }
    }

    // Getters y Setters
    public String getSagaId() {
        return sagaId;
    }

    public void setSagaId(String sagaId) {
        this.sagaId = sagaId;
    }

    public String getCorrelationId() {
        return correlationId;
    }

    public void setCorrelationId(String correlationId) {
        this.correlationId = correlationId;
    }

    public String getEventType() {
        return eventType;
    }

    public void setEventType(String eventType) {
        this.eventType = eventType;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }

    public String getSourceService() {
        return sourceService;
    }

    public void setSourceService(String sourceService) {
        this.sourceService = sourceService;
    }

    public String getTargetTopic() {
        return targetTopic;
    }

    public void setTargetTopic(String targetTopic) {
        this.targetTopic = targetTopic;
    }

    public Payload getPayload() {
        return payload;
    }

    public void setPayload(Payload payload) {
        this.payload = payload;
    }
}
