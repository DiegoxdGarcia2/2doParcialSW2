package com.aegiscore.actuarial.application;

import com.aegiscore.actuarial.application.dto.IniciarLiquidacionCommand;
import com.aegiscore.actuarial.application.dto.LiquidacionSagaResponseDTO;
import com.aegiscore.actuarial.application.dto.SagaEventDTO;
import com.aegiscore.actuarial.application.ports.out.OrdenLiquidacionRepositoryPort;
import com.aegiscore.actuarial.application.ports.out.ReservaTecnicaRepositoryPort;
import com.aegiscore.actuarial.application.ports.out.SagaEventPublisherPort;
import com.aegiscore.actuarial.application.service.SagaLiquidacionOrchestratorService;
import com.aegiscore.actuarial.domain.model.liquidacion.EstadoSaga;
import com.aegiscore.actuarial.domain.model.liquidacion.OrdenLiquidacion;
import com.aegiscore.actuarial.domain.model.reserva.ReservaTecnica;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@DisplayName("Pruebas Unitarias del Orquestador Saga: SagaLiquidacionOrchestratorService (CU09)")
class SagaLiquidacionOrchestratorServiceTest {

    private OrdenLiquidacionRepositoryPort ordenRepository;
    private ReservaTecnicaRepositoryPort reservaRepository;
    private SagaEventPublisherPort eventPublisher;
    private SagaLiquidacionOrchestratorService orchestrator;

    @BeforeEach
    void setUp() {
        ordenRepository = mock(OrdenLiquidacionRepositoryPort.class);
        reservaRepository = mock(ReservaTecnicaRepositoryPort.class);
        eventPublisher = mock(SagaEventPublisherPort.class);
        orchestrator = new SagaLiquidacionOrchestratorService(ordenRepository, reservaRepository, eventPublisher);
    }

    @Test
    @DisplayName("Debe iniciar la Saga, persistir orden en estado INICIADA y publicar comando a MS2 (NestJS)")
    void debeIniciarSagaYPublicarComandoPaso1() {
        IniciarLiquidacionCommand command = new IniciarLiquidacionCommand(
                "REC-2026-00492",
                UUID.randomUUID(),
                UUID.randomUUID(),
                new BigDecimal("3000.00"),
                "1000002938481"
        );

        when(ordenRepository.guardar(any(OrdenLiquidacion.class))).thenAnswer(i -> i.getArgument(0));

        LiquidacionSagaResponseDTO response = orchestrator.iniciarLiquidacion(command);

        assertNotNull(response);
        assertNotNull(response.getSagaId());
        assertEquals("INICIADA", response.getEstadoSaga());
        assertEquals(new BigDecimal("300.00"), response.getDeducibleAplicado()); // 10% de 3000
        assertEquals(new BigDecimal("2700.00"), response.getMontoNetoDesembolso()); // 3000 - 300

        verify(ordenRepository, atLeastOnce()).guardar(any(OrdenLiquidacion.class));
        verify(eventPublisher, times(1)).publicarComando(eq("aegiscore.saga.commands"), any(SagaEventDTO.class));
        verify(eventPublisher, times(1)).publicarEvento(eq("aegiscore.saga.events"), any(SagaEventDTO.class));
    }

    @Test
    @DisplayName("Paso 1 -> Paso 2: Debe avanzar a PASO1_SINIESTRO_BLOQUEADO y emitir comando hacia MS1 (PHP)")
    void debeProcesarRespuestaPaso1SiniestroBloqueado() {
        String sagaId = "SAGA-TEST-123";
        OrdenLiquidacion orden = new OrdenLiquidacion(
                UUID.randomUUID(), sagaId, "REC-1", UUID.randomUUID(), UUID.randomUUID(),
                new BigDecimal("2000.00"), new BigDecimal("200.00"), new BigDecimal("1800.00"),
                EstadoSaga.INICIADA, "CTA-1", Instant.now()
        );

        when(ordenRepository.buscarPorSagaId(sagaId)).thenReturn(Optional.of(orden));
        when(ordenRepository.guardar(any(OrdenLiquidacion.class))).thenAnswer(i -> i.getArgument(0));

        SagaEventDTO event = new SagaEventDTO(sagaId, "CORR-1", "ReclamoMarcadoEnLiquidacionEvent", "aegiscore.saga.events", new SagaEventDTO.Payload());
        orchestrator.procesarRespuestaPaso1SiniestroBloqueado(event);

        assertEquals(EstadoSaga.PASO1_SINIESTRO_BLOQUEADO, orden.getEstadoSaga());
        ArgumentCaptor<SagaEventDTO> captor = ArgumentCaptor.forClass(SagaEventDTO.class);
        verify(eventPublisher).publicarComando(eq("aegiscore.saga.commands"), captor.capture());
        assertEquals("DescontarCoberturaPolizaCommand", captor.getValue().getEventType());
    }

    @Test
    @DisplayName("Paso 2 -> Paso 3 Exitoso: Con reserva suficiente, emite pago y completa la Saga (CU09 Éxito)")
    void debeCompletarSagaCuandoReservaEsSuficiente() {
        String sagaId = "SAGA-TEST-456";
        OrdenLiquidacion orden = new OrdenLiquidacion(
                UUID.randomUUID(), sagaId, "REC-2", UUID.randomUUID(), UUID.randomUUID(),
                new BigDecimal("2500.00"), new BigDecimal("250.00"), new BigDecimal("2250.00"),
                EstadoSaga.PASO1_SINIESTRO_BLOQUEADO, "CTA-2", Instant.now()
        );

        ReservaTecnica reserva = new ReservaTecnica(
                UUID.randomUUID(), "2026-10", new BigDecimal("500000.00"), new BigDecimal("100000.00")
        );

        when(ordenRepository.buscarPorSagaId(sagaId)).thenReturn(Optional.of(orden));
        when(reservaRepository.obtenerReservaActual()).thenReturn(Optional.of(reserva));
        when(ordenRepository.guardar(any(OrdenLiquidacion.class))).thenAnswer(i -> i.getArgument(0));

        SagaEventDTO.Payload payload = new SagaEventDTO.Payload();
        payload.setMontoNetoDesembolso(orden.getMontoNetoDesembolso());
        SagaEventDTO event = new SagaEventDTO(sagaId, "CORR-2", "CoberturaPolizaDescontadaEvent", "aegiscore.saga.events", payload);

        orchestrator.procesarRespuestaPaso2CoberturaDescontada(event);

        assertEquals(EstadoSaga.SAGA_COMPLETADA, orden.getEstadoSaga());
        assertNotNull(orden.getComprobanteTransferencia());

        ArgumentCaptor<SagaEventDTO> captor = ArgumentCaptor.forClass(SagaEventDTO.class);
        verify(eventPublisher).publicarEvento(eq("aegiscore.saga.events"), captor.capture());
        assertEquals("SagaLiquidacionCompletadaEvent", captor.getValue().getEventType());
    }

    @Test
    @DisplayName("Paso 3 Fallido -> ROLLBACK: Si la reserva es insuficiente, dispara compensaciones en Kafka")
    void debeDispararRollbackCompensatorioSiReservaEsInsuficiente() {
        String sagaId = "SAGA-TEST-FAIL-789";
        OrdenLiquidacion orden = new OrdenLiquidacion(
                UUID.randomUUID(), sagaId, "REC-3", UUID.randomUUID(), UUID.randomUUID(),
                new BigDecimal("50000.00"), new BigDecimal("5000.00"), new BigDecimal("45000.00"),
                EstadoSaga.PASO1_SINIESTRO_BLOQUEADO, "CTA-3", Instant.now()
        );

        // Reserva técnica insuficiente: 120,000 - 45,000 = 75,000 < 100,000 (Límite mínimo)
        ReservaTecnica reservaInsuficiente = new ReservaTecnica(
                UUID.randomUUID(), "2026-10", new BigDecimal("120000.00"), new BigDecimal("100000.00")
        );

        when(ordenRepository.buscarPorSagaId(sagaId)).thenReturn(Optional.of(orden));
        when(reservaRepository.obtenerReservaActual()).thenReturn(Optional.of(reservaInsuficiente));
        when(ordenRepository.guardar(any(OrdenLiquidacion.class))).thenAnswer(i -> i.getArgument(0));

        SagaEventDTO.Payload payload = new SagaEventDTO.Payload();
        payload.setMontoNetoDesembolso(orden.getMontoNetoDesembolso());
        SagaEventDTO event = new SagaEventDTO(sagaId, "CORR-3", "CoberturaPolizaDescontadaEvent", "aegiscore.saga.events", payload);

        orchestrator.procesarRespuestaPaso2CoberturaDescontada(event);

        // Debe quedar en estado SAGA_FALLIDA_COMPENSADA
        assertEquals(EstadoSaga.SAGA_FALLIDA_COMPENSADA, orden.getEstadoSaga());
        assertNotNull(orden.getMotivoCompensacion());

        // Se deben emitir 3 mensajes al tópico de compensación:
        // 1. CompensarCoberturaCommand hacia MS1 (PHP)
        // 2. RevertirEstadoReclamoCommand hacia MS2 (NestJS)
        // 3. SagaLiquidacionFallidaCompensadaEvent (hacia n8n)
        verify(eventPublisher, times(3)).publicarCompensacion(eq("aegiscore.saga.compensations"), any(SagaEventDTO.class));
    }
}
