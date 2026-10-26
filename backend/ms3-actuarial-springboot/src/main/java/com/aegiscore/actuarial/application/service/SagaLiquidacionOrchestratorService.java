package com.aegiscore.actuarial.application.service;

import com.aegiscore.actuarial.application.dto.IniciarLiquidacionCommand;
import com.aegiscore.actuarial.application.dto.LiquidacionSagaResponseDTO;
import com.aegiscore.actuarial.application.dto.SagaEventDTO;
import com.aegiscore.actuarial.application.ports.in.ConsultarSagaUseCasePort;
import com.aegiscore.actuarial.application.ports.in.IniciarLiquidacionSagaUseCasePort;
import com.aegiscore.actuarial.application.ports.in.ProcesarPasoSagaUseCasePort;
import com.aegiscore.actuarial.application.ports.out.OrdenLiquidacionRepositoryPort;
import com.aegiscore.actuarial.application.ports.out.ReservaTecnicaRepositoryPort;
import com.aegiscore.actuarial.application.ports.out.SagaEventPublisherPort;
import com.aegiscore.actuarial.domain.exception.SagaInvalidaException;
import com.aegiscore.actuarial.domain.model.liquidacion.EstadoSaga;
import com.aegiscore.actuarial.domain.model.liquidacion.OrdenLiquidacion;
import com.aegiscore.actuarial.domain.model.reserva.ReservaTecnica;
import com.aegiscore.actuarial.domain.service.CalculoActuarialService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

/**
 * Servicio Orquestador del Patrón Saga (CU09: Liquidación y Pago en 3 Microservicios).
 * Coordina el flujo distribuido a través de Kafka (commands, events, compensations).
 */
@Service
public class SagaLiquidacionOrchestratorService implements
        IniciarLiquidacionSagaUseCasePort,
        ProcesarPasoSagaUseCasePort,
        ConsultarSagaUseCasePort {

    private static final String TOPIC_COMMANDS = "aegiscore.saga.commands";
    private static final String TOPIC_EVENTS = "aegiscore.saga.events";
    private static final String TOPIC_COMPENSATIONS = "aegiscore.saga.compensations";

    private final OrdenLiquidacionRepositoryPort ordenRepository;
    private final ReservaTecnicaRepositoryPort reservaRepository;
    private final SagaEventPublisherPort eventPublisher;
    private final CalculoActuarialService calculoActuarialService;

    public SagaLiquidacionOrchestratorService(
            OrdenLiquidacionRepositoryPort ordenRepository,
            ReservaTecnicaRepositoryPort reservaRepository,
            SagaEventPublisherPort eventPublisher
    ) {
        this.ordenRepository = ordenRepository;
        this.reservaRepository = reservaRepository;
        this.eventPublisher = eventPublisher;
        this.calculoActuarialService = new CalculoActuarialService();
    }

    @Override
    @Transactional
    public LiquidacionSagaResponseDTO iniciarLiquidacion(IniciarLiquidacionCommand command) {
        String sagaId = UUID.randomUUID().toString();

        BigDecimal deducible = calculoActuarialService.calcularDeducible(
                command.getMontoIndemnizacion(),
                new BigDecimal("10.00"),
                new BigDecimal("150.00")
        );
        BigDecimal montoNeto = calculoActuarialService.calcularMontoNetoDesembolso(
                command.getMontoIndemnizacion(),
                deducible
        );

        OrdenLiquidacion orden = new OrdenLiquidacion(
                UUID.randomUUID(),
                sagaId,
                command.getReclamoIdMongo(),
                command.getPolizaId(),
                command.getClienteId(),
                command.getMontoIndemnizacion(),
                deducible,
                montoNeto,
                EstadoSaga.INICIADA,
                command.getCuentaBancariaDestino(),
                Instant.now()
        );

        ordenRepository.guardar(orden);

        // Publicar evento de inicio
        SagaEventDTO.Payload payload = new SagaEventDTO.Payload();
        payload.setReclamoId(command.getReclamoIdMongo());
        payload.setPolizaId(command.getPolizaId().toString());
        payload.setClienteId(command.getClienteId().toString());
        payload.setMontoIndemnizacion(command.getMontoIndemnizacion());
        payload.setDeducibleAplicado(deducible);
        payload.setMontoNetoDesembolso(montoNeto);
        payload.setCuentaBancariaDestino(command.getCuentaBancariaDestino());

        SagaEventDTO inicioEvent = new SagaEventDTO(sagaId, UUID.randomUUID().toString(), "SagaLiquidacionIniciadaEvent", TOPIC_EVENTS, payload);
        eventPublisher.publicarEvento(TOPIC_EVENTS, inicioEvent);

        // PASO 1: Emitir comando hacia MS2 NestJS para bloquear el reclamo
        SagaEventDTO paso1Command = new SagaEventDTO(sagaId, UUID.randomUUID().toString(), "MarcarReclamoEnLiquidacionCommand", TOPIC_COMMANDS, payload);
        eventPublisher.publicarComando(TOPIC_COMMANDS, paso1Command);

        // Si se solicitó simulación forzada de fallo en Paso 3 (para testing de compensación)
        if (command.isSimularFalloReserva()) {
            orden.iniciarCompensacion("Simulación intencional de fallo de reserva técnica para demostración");
            ordenRepository.guardar(orden);
        }

        return mapearADTO(orden, "Saga de Liquidación iniciada exitosamente en Kafka.");
    }

    @Override
    @Transactional
    public void procesarRespuestaPaso1SiniestroBloqueado(SagaEventDTO event) {
        OrdenLiquidacion orden = obtenerOrdenPorSagaId(event.getSagaId());
        orden.registrarPaso1SiniestroBloqueado();
        ordenRepository.guardar(orden);

        // PASO 2: Emitir comando hacia MS1 PHP Laravel para descontar cobertura de la póliza
        SagaEventDTO.Payload payload = event.getPayload();
        SagaEventDTO paso2Command = new SagaEventDTO(
                orden.getSagaId(),
                event.getCorrelationId(),
                "DescontarCoberturaPolizaCommand",
                TOPIC_COMMANDS,
                payload
        );
        eventPublisher.publicarComando(TOPIC_COMMANDS, paso2Command);
    }

    @Override
    @Transactional
    public void procesarRespuestaPaso2CoberturaDescontada(SagaEventDTO event) {
        OrdenLiquidacion orden = obtenerOrdenPorSagaId(event.getSagaId());
        orden.registrarPaso2CoberturaDescontada();
        ordenRepository.guardar(orden);

        // PASO 3: Validación actuarial de la reserva técnica y desembolso en Spring Boot
        Optional<ReservaTecnica> reservaOpt = reservaRepository.obtenerReservaActual();
        boolean fondosSuficientes = reservaOpt.isPresent()
                && reservaOpt.get().puedeCubrirDesembolso(orden.getMontoNetoDesembolso())
                && !orden.estaEnCompensacion();

        if (fondosSuficientes) {
            ReservaTecnica reserva = reservaOpt.get();
            reserva.descontarDesembolso(orden.getMontoNetoDesembolso());
            reservaRepository.guardar(reserva);

            String comprobante = "TRF-ACT-" + System.currentTimeMillis();
            orden.registrarPaso3DesembolsoCompletado(comprobante);
            orden.marcarCompletada();
            ordenRepository.guardar(orden);

            // Publicar evento final de completitud (consumido por n8n para factura/correo al asegurado)
            SagaEventDTO.Payload payload = event.getPayload();
            payload.setComprobanteId(comprobante);
            SagaEventDTO completadaEvent = new SagaEventDTO(
                    orden.getSagaId(),
                    event.getCorrelationId(),
                    "SagaLiquidacionCompletadaEvent",
                    TOPIC_EVENTS,
                    payload
            );
            eventPublisher.publicarEvento(TOPIC_EVENTS, completadaEvent);

        } else {
            // FALLO EN PASO 3 -> DISPARAR ROLLBACK COMPENSATORIO
            String motivo = reservaOpt.isEmpty()
                    ? "Reserva técnica no encontrada"
                    : "Fondos de reserva técnica insuficientes para cubrir " + orden.getMontoNetoDesembolso() + " USD";
            procesarFalloYCompensar(orden.getSagaId(), motivo);
        }
    }

    @Override
    @Transactional
    public void procesarFalloYCompensar(String sagaId, String motivoFallo) {
        OrdenLiquidacion orden = obtenerOrdenPorSagaId(sagaId);
        orden.iniciarCompensacion(motivoFallo);
        ordenRepository.guardar(orden);

        SagaEventDTO.Payload payload = new SagaEventDTO.Payload();
        payload.setReclamoId(orden.getReclamoIdMongo());
        payload.setPolizaId(orden.getPolizaId().toString());
        payload.setClienteId(orden.getClienteId().toString());
        payload.setMontoIndemnizacion(orden.getMontoIndemnizacion());
        payload.setMontoNetoDesembolso(orden.getMontoNetoDesembolso());
        payload.setMotivoRechazo(motivoFallo);

        // 1. Compensar MS1 PHP: Restituir cobertura
        SagaEventDTO compensarCobertura = new SagaEventDTO(
                sagaId,
                UUID.randomUUID().toString(),
                "CompensarCoberturaCommand",
                TOPIC_COMPENSATIONS,
                payload
        );
        eventPublisher.publicarCompensacion(TOPIC_COMPENSATIONS, compensarCobertura);

        // 2. Compensar MS2 NestJS: Revertir estado del reclamo a OBSERVADO_FINANZAS
        orden.marcarSiniestroCompensando();
        SagaEventDTO revertirSiniestro = new SagaEventDTO(
                sagaId,
                UUID.randomUUID().toString(),
                "RevertirEstadoReclamoCommand",
                TOPIC_COMPENSATIONS,
                payload
        );
        eventPublisher.publicarCompensacion(TOPIC_COMPENSATIONS, revertirSiniestro);

        // 3. Marcar Saga Fallida Compensada y notificar en Kafka (consumido por n8n para alertar auditoría)
        orden.marcarSagaFallidaCompensada();
        ordenRepository.guardar(orden);

        SagaEventDTO sagaFallidaEvent = new SagaEventDTO(
                sagaId,
                UUID.randomUUID().toString(),
                "SagaLiquidacionFallidaCompensadaEvent",
                TOPIC_COMPENSATIONS,
                payload
        );
        eventPublisher.publicarCompensacion(TOPIC_COMPENSATIONS, sagaFallidaEvent);
    }

    @Override
    public LiquidacionSagaResponseDTO consultarPorSagaId(String sagaId) {
        OrdenLiquidacion orden = obtenerOrdenPorSagaId(sagaId);
        return mapearADTO(orden, "Consulta de estado Saga exitosa.");
    }

    private OrdenLiquidacion obtenerOrdenPorSagaId(String sagaId) {
        return ordenRepository.buscarPorSagaId(sagaId)
                .orElseThrow(() -> new SagaInvalidaException("No se encontró la instancia Saga: " + sagaId));
    }

    private LiquidacionSagaResponseDTO mapearADTO(OrdenLiquidacion orden, String mensaje) {
        LiquidacionSagaResponseDTO dto = new LiquidacionSagaResponseDTO();
        dto.setSagaId(orden.getSagaId());
        dto.setReclamoIdMongo(orden.getReclamoIdMongo());
        dto.setPolizaId(orden.getPolizaId());
        dto.setMontoIndemnizacion(orden.getMontoIndemnizacion());
        dto.setDeducibleAplicado(orden.getDeducibleAplicado());
        dto.setMontoNetoDesembolso(orden.getMontoNetoDesembolso());
        dto.setEstadoSaga(orden.getEstadoSaga().name());
        dto.setComprobanteTransferencia(orden.getComprobanteTransferencia());
        dto.setMotivoCompensacion(orden.getMotivoCompensacion());
        dto.setMensaje(mensaje);
        dto.setFechaInicio(orden.getFechaInicio());
        dto.setFechaFinalizacion(orden.getFechaFinalizacion());
        return dto;
    }
}
