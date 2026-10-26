package com.aegiscore.actuarial.application.service;

import com.aegiscore.actuarial.application.dto.ConfirmarPagoQRCommand;
import com.aegiscore.actuarial.application.dto.GenerarCobroQRCommand;
import com.aegiscore.actuarial.application.dto.PagoQRResponseDTO;
import com.aegiscore.actuarial.application.ports.in.CobroPrimaQRUseCasePort;
import com.aegiscore.actuarial.application.ports.out.IdempotencyLockPort;
import com.aegiscore.actuarial.application.ports.out.PagoPrimaRepositoryPort;
import com.aegiscore.actuarial.domain.exception.IdempotencyConflictException;
import com.aegiscore.actuarial.domain.model.cobranza.MetodoPago;
import com.aegiscore.actuarial.domain.model.cobranza.PagoPrima;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Base64;
import java.util.Optional;
import java.util.UUID;

/**
 * Servicio de Aplicación: CobranzaPrimaQRService (CU10).
 * Procesa cobros de primas y pagos QR con control de Idempotencia respaldado por DynamoDB.
 */
@Service
public class CobranzaPrimaQRService implements CobroPrimaQRUseCasePort {

    private final PagoPrimaRepositoryPort pagoRepository;
    private final IdempotencyLockPort idempotencyLockPort;
    private final ObjectMapper objectMapper;

    public CobranzaPrimaQRService(
            PagoPrimaRepositoryPort pagoRepository,
            IdempotencyLockPort idempotencyLockPort
    ) {
        this.pagoRepository = pagoRepository;
        this.idempotencyLockPort = idempotencyLockPort;
        this.objectMapper = new ObjectMapper().findAndRegisterModules();
    }

    @Override
    @Transactional
    public PagoQRResponseDTO generarOrdenCobroQR(GenerarCobroQRCommand command, String idempotencyKey) {
        String key = (idempotencyKey != null && !idempotencyKey.isBlank())
                ? idempotencyKey
                : UUID.randomUUID().toString();

        // Generar payload simulado de QR interoperable
        String qrPayloadRaw = String.format(
                "AEGISCORE-QR|POLIZA:%s|CUOTA:%d|MONTO:%.2f|CUR:%s|VENC:%d",
                command.getPolizaId(),
                command.getNumeroCuota(),
                command.getMonto(),
                command.getMoneda(),
                System.currentTimeMillis() + (86400 * 1000)
        );
        String qrBase64 = Base64.getEncoder().encodeToString(qrPayloadRaw.getBytes(StandardCharsets.UTF_8));

        PagoPrima pago = new PagoPrima(
                UUID.randomUUID(),
                command.getPolizaId(),
                command.getNumeroCuota(),
                command.getMonto(),
                command.getMoneda(),
                MetodoPago.QR_SIMPLE,
                key,
                qrBase64
        );

        pagoRepository.guardar(pago);

        return mapearADTO(pago, "Orden de cobro QR generada correctamente. Escanee el código para pagar.");
    }

    @Override
    @Transactional
    public PagoQRResponseDTO confirmarPagoQR(ConfirmarPagoQRCommand command, String idempotencyKey) {
        if (idempotencyKey == null || idempotencyKey.isBlank()) {
            throw new IllegalArgumentException("La cabecera Idempotency-Key es obligatoria para confirmar pagos.");
        }

        String payloadHash = calcularSha256(command);

        // 1. Control de Idempotencia contra DynamoDB
        Optional<IdempotencyLockPort.IdempotencyRecordDTO> recordOpt = idempotencyLockPort.consultarRegistro(idempotencyKey);
        if (recordOpt.isPresent()) {
            IdempotencyLockPort.IdempotencyRecordDTO record = recordOpt.get();
            if ("COMPLETED".equals(record.status()) && record.responseBodyCached() != null) {
                try {
                    // Replay instantáneo (<5ms)
                    PagoQRResponseDTO cachedResponse = objectMapper.readValue(record.responseBodyCached(), PagoQRResponseDTO.class);
                    cachedResponse.setMensaje("Pago procesado previamente (Respuesta idempotente recuperada de DynamoDB).");
                    return cachedResponse;
                } catch (Exception ignored) {
                }
            } else if ("PROCESSING".equals(record.status())) {
                throw new IdempotencyConflictException("Una transacción con esta Idempotency-Key ya está en proceso.");
            }
        }

        // Adquirir bloqueo en DynamoDB
        idempotencyLockPort.intentarBloqueo(idempotencyKey, payloadHash);

        // 2. Procesar el pago en PostgreSQL
        Optional<PagoPrima> pagoOpt = pagoRepository.buscarPorIdempotencyKey(idempotencyKey);
        PagoPrima pago;
        if (pagoOpt.isPresent()) {
            pago = pagoOpt.get();
        } else {
            pago = new PagoPrima(
                    UUID.randomUUID(),
                    command.getPolizaId(),
                    command.getNumeroCuota(),
                    command.getMonto(),
                    "USD",
                    MetodoPago.QR_SIMPLE,
                    idempotencyKey,
                    null
            );
        }

        String codigoAuth = (command.getCodigoAutorizacionBancaria() != null && !command.getCodigoAutorizacionBancaria().isBlank())
                ? command.getCodigoAutorizacionBancaria()
                : "AUTH-BCB-" + System.currentTimeMillis();

        pago.confirmarPagoExitoso(codigoAuth);
        pagoRepository.guardar(pago);

        PagoQRResponseDTO response = mapearADTO(pago, "Pago QR confirmado y registrado con éxito.");

        // 3. Completar bloqueo en DynamoDB con el JSON de respuesta cacheado
        try {
            String jsonCached = objectMapper.writeValueAsString(response);
            idempotencyLockPort.completarBloqueo(idempotencyKey, 200, jsonCached);
        } catch (Exception e) {
            idempotencyLockPort.completarBloqueo(idempotencyKey, 200, "{\"status\":\"OK\"}");
        }

        return response;
    }

    private String calcularSha256(Object object) {
        try {
            String json = objectMapper.writeValueAsString(object);
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(json.getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (Exception e) {
            return UUID.randomUUID().toString();
        }
    }

    private PagoQRResponseDTO mapearADTO(PagoPrima pago, String mensaje) {
        PagoQRResponseDTO dto = new PagoQRResponseDTO();
        dto.setPagoId(pago.getId());
        dto.setPolizaId(pago.getPolizaId());
        dto.setNumeroCuota(pago.getNumeroCuota());
        dto.setMonto(pago.getMonto());
        dto.setMoneda(pago.getMoneda());
        dto.setMetodoPago(pago.getMetodoPago().name());
        dto.setIdempotencyKey(pago.getIdempotencyKey());
        dto.setQrImagenPayload(pago.getQrImagenPayload());
        dto.setCodigoAutorizacionBancaria(pago.getCodigoAutorizacionBancaria());
        dto.setEstado(pago.getEstado().name());
        dto.setFechaPago(pago.getFechaPago());
        dto.setMensaje(mensaje);
        return dto;
    }
}
