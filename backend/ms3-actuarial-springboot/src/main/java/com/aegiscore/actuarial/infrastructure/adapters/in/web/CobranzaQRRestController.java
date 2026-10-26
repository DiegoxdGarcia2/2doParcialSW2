package com.aegiscore.actuarial.infrastructure.adapters.in.web;

import com.aegiscore.actuarial.application.dto.ConfirmarPagoQRCommand;
import com.aegiscore.actuarial.application.dto.GenerarCobroQRCommand;
import com.aegiscore.actuarial.application.dto.PagoQRResponseDTO;
import com.aegiscore.actuarial.application.ports.in.CobroPrimaQRUseCasePort;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * Adaptador Web REST de Entrada: CobranzaQRRestController (CU10).
 * Maneja la generación y cobro idempotente de primas respaldado por DynamoDB y PostgreSQL.
 */
@RestController
@RequestMapping("/api/v1/cobranzas/qr")
@CrossOrigin(origins = "*")
public class CobranzaQRRestController {

    private final CobroPrimaQRUseCasePort cobroPrimaQRUseCase;

    public CobranzaQRRestController(CobroPrimaQRUseCasePort cobroPrimaQRUseCase) {
        this.cobroPrimaQRUseCase = cobroPrimaQRUseCase;
    }

    @PostMapping("/generar")
    public ResponseEntity<PagoQRResponseDTO> generarCobroQR(
            @RequestBody GenerarCobroQRCommand command,
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey
    ) {
        PagoQRResponseDTO response = cobroPrimaQRUseCase.generarOrdenCobroQR(command, idempotencyKey);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/confirmar")
    public ResponseEntity<PagoQRResponseDTO> confirmarPagoQR(
            @RequestBody ConfirmarPagoQRCommand command,
            @RequestHeader(value = "Idempotency-Key") String idempotencyKey
    ) {
        PagoQRResponseDTO response = cobroPrimaQRUseCase.confirmarPagoQR(command, idempotencyKey);

        HttpHeaders headers = new HttpHeaders();
        if (response.getMensaje() != null && response.getMensaje().contains("DynamoDB")) {
            headers.add("X-Cache-Lookup", "HIT_IDEMPOTENCY_DYNAMODB");
        }

        return ResponseEntity.ok().headers(headers).body(response);
    }
}
