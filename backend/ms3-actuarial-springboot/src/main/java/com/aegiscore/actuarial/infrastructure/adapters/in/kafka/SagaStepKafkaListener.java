package com.aegiscore.actuarial.infrastructure.adapters.in.kafka;

import com.aegiscore.actuarial.application.dto.SagaEventDTO;
import com.aegiscore.actuarial.application.ports.in.ProcesarPasoSagaUseCasePort;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

/**
 * Adaptador de entrada Kafka para la orquestación del Patrón Saga (CU09).
 * Escucha las respuestas de los microservicios colaboradores (MS2 NestJS y MS1 PHP).
 */
@Component
public class SagaStepKafkaListener {

    private static final Logger log = LoggerFactory.getLogger(SagaStepKafkaListener.class);

    private final ProcesarPasoSagaUseCasePort procesarPasoUseCase;
    private final ObjectMapper objectMapper;

    public SagaStepKafkaListener(ProcesarPasoSagaUseCasePort procesarPasoUseCase) {
        this.procesarPasoUseCase = procesarPasoUseCase;
        this.objectMapper = new ObjectMapper().findAndRegisterModules();
    }

    @KafkaListener(
            topics = "aegiscore.saga.events",
            groupId = "${spring.kafka.consumer.group-id:ms3-saga-orchestrator-group}"
    )
    public void consumirEventoRespuesta(String mensajeJson) {
        try {
            SagaEventDTO event = objectMapper.readValue(mensajeJson, SagaEventDTO.class);
            log.info("[SAGA KAFKA LISTENER] Mensaje recibido -> EventType: {}, SagaId: {}, Source: {}",
                    event.getEventType(), event.getSagaId(), event.getSourceService());

            switch (event.getEventType()) {
                case "ReclamoMarcadoEnLiquidacionEvent" -> {
                    log.info("[SAGA ORQUESTADOR] Paso 1 completado por MS2 NestJS. Avanzando a Paso 2 (PHP)...");
                    procesarPasoUseCase.procesarRespuestaPaso1SiniestroBloqueado(event);
                }
                case "CoberturaPolizaDescontadaEvent" -> {
                    log.info("[SAGA ORQUESTADOR] Paso 2 completado por MS1 PHP. Avanzando a Paso 3 (Reserva Actuarial)...");
                    procesarPasoUseCase.procesarRespuestaPaso2CoberturaDescontada(event);
                }
                case "ReclamoBloqueoFallidoEvent", "DescuentoCoberturaFallidoEvent" -> {
                    String motivo = event.getPayload() != null && event.getPayload().getMotivoRechazo() != null
                            ? event.getPayload().getMotivoRechazo()
                            : "Fallo reportado en paso intermedio de la Saga";
                    log.warn("[SAGA ORQUESTADOR] Fallo reportado por microservicio colaborador en Saga {}. Disparando Rollback...", event.getSagaId());
                    procesarPasoUseCase.procesarFalloYCompensar(event.getSagaId(), motivo);
                }
                default -> {
                    // Otros eventos del tópico no dirigidos al flujo secuencial del orquestador
                }
            }
        } catch (Exception e) {
            log.error("[SAGA KAFKA LISTENER] Error al procesar mensaje de evento Saga: {}", e.getMessage());
        }
    }
}
