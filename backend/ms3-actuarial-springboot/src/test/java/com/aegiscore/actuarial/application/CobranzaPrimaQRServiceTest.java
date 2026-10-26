package com.aegiscore.actuarial.application;

import com.aegiscore.actuarial.application.dto.ConfirmarPagoQRCommand;
import com.aegiscore.actuarial.application.dto.GenerarCobroQRCommand;
import com.aegiscore.actuarial.application.dto.PagoQRResponseDTO;
import com.aegiscore.actuarial.application.ports.out.IdempotencyLockPort;
import com.aegiscore.actuarial.application.ports.out.PagoPrimaRepositoryPort;
import com.aegiscore.actuarial.application.service.CobranzaPrimaQRService;
import com.aegiscore.actuarial.domain.model.cobranza.PagoPrima;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@DisplayName("Pruebas Unitarias de Cobranza QR e Idempotencia: CobranzaPrimaQRService (CU10)")
class CobranzaPrimaQRServiceTest {

    private PagoPrimaRepositoryPort pagoRepository;
    private IdempotencyLockPort idempotencyLockPort;
    private CobranzaPrimaQRService cobranzaService;

    @BeforeEach
    void setUp() {
        pagoRepository = mock(PagoPrimaRepositoryPort.class);
        idempotencyLockPort = mock(IdempotencyLockPort.class);
        cobranzaService = new CobranzaPrimaQRService(pagoRepository, idempotencyLockPort);
    }

    @Test
    @DisplayName("Debe generar orden de cobro QR con estado PENDIENTE y payload codificado")
    void debeGenerarOrdenCobroQRExitosamente() {
        GenerarCobroQRCommand command = new GenerarCobroQRCommand(
                UUID.randomUUID(), 3, new BigDecimal("120.00"), "USD"
        );
        String key = UUID.randomUUID().toString();

        when(pagoRepository.guardar(any(PagoPrima.class))).thenAnswer(i -> i.getArgument(0));

        PagoQRResponseDTO response = cobranzaService.generarOrdenCobroQR(command, key);

        assertNotNull(response);
        assertEquals(new BigDecimal("120.00"), response.getMonto());
        assertEquals("PENDIENTE", response.getEstado());
        assertNotNull(response.getQrImagenPayload());
        verify(pagoRepository).guardar(any(PagoPrima.class));
    }

    @Test
    @DisplayName("Debe confirmar pago QR por primera vez, guardar en Postgres y registrar en DynamoDB")
    void debeConfirmarPagoQRPrimerIntento() {
        String key = UUID.randomUUID().toString();
        ConfirmarPagoQRCommand command = new ConfirmarPagoQRCommand(
                UUID.randomUUID(), 1, new BigDecimal("85.00"), "AUTH-BANK-99"
        );

        when(idempotencyLockPort.consultarRegistro(key)).thenReturn(Optional.empty());
        when(pagoRepository.buscarPorIdempotencyKey(key)).thenReturn(Optional.empty());
        when(pagoRepository.guardar(any(PagoPrima.class))).thenAnswer(i -> i.getArgument(0));

        PagoQRResponseDTO response = cobranzaService.confirmarPagoQR(command, key);

        assertNotNull(response);
        assertEquals("EXITOSO", response.getEstado());
        assertEquals("AUTH-BANK-99", response.getCodigoAutorizacionBancaria());

        verify(idempotencyLockPort).intentarBloqueo(eq(key), any());
        verify(idempotencyLockPort).completarBloqueo(eq(key), eq(200), any());
        verify(pagoRepository).guardar(any(PagoPrima.class));
    }

    @Test
    @DisplayName("Reintento con misma Idempotency-Key: Debe recuperar respuesta de DynamoDB sin duplicar cobro")
    void debeRetornarRespuestaEnCacheAnteReintentoIdempotente() {
        String key = "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d";
        ConfirmarPagoQRCommand command = new ConfirmarPagoQRCommand(
                UUID.randomUUID(), 1, new BigDecimal("85.00"), "AUTH-BANK-99"
        );

        String jsonCached = "{\"pagoId\":\"" + UUID.randomUUID() + "\",\"estado\":\"EXITOSO\",\"monto\":85.00,\"mensaje\":\"OK\"}";
        IdempotencyLockPort.IdempotencyRecordDTO cachedRecord = new IdempotencyLockPort.IdempotencyRecordDTO(
                key, "hash123", "COMPLETED", 200, jsonCached
        );

        when(idempotencyLockPort.consultarRegistro(key)).thenReturn(Optional.of(cachedRecord));

        PagoQRResponseDTO response = cobranzaService.confirmarPagoQR(command, key);

        assertNotNull(response);
        assertEquals("EXITOSO", response.getEstado());
        assertTrue(response.getMensaje().contains("DynamoDB"));

        // No debe intentar guardar en la base de datos relacional de nuevo
        verify(pagoRepository, never()).guardar(any(PagoPrima.class));
    }
}
