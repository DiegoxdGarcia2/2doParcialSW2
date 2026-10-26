package com.aegiscore.actuarial.infrastructure.adapters.in.web;

import com.aegiscore.actuarial.application.dto.IniciarLiquidacionCommand;
import com.aegiscore.actuarial.application.dto.LiquidacionSagaResponseDTO;
import com.aegiscore.actuarial.application.ports.in.ConsultarSagaUseCasePort;
import com.aegiscore.actuarial.application.ports.in.IniciarLiquidacionSagaUseCasePort;
import com.aegiscore.actuarial.application.ports.in.ProcesarPasoSagaUseCasePort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * Adaptador Web REST de Entrada: LiquidacionRestController (CU09).
 * Punto de entrada para que el Ajustador o Frontend Angular inicie la transacción Saga en 3 microservicios.
 */
@RestController
@RequestMapping("/api/v1/liquidaciones/saga")
@CrossOrigin(origins = "*")
public class LiquidacionRestController {

    private final IniciarLiquidacionSagaUseCasePort iniciarSagaUseCase;
    private final ConsultarSagaUseCasePort consultarSagaUseCase;
    private final ProcesarPasoSagaUseCasePort procesarPasoUseCase;

    public LiquidacionRestController(
            IniciarLiquidacionSagaUseCasePort iniciarSagaUseCase,
            ConsultarSagaUseCasePort consultarSagaUseCase,
            ProcesarPasoSagaUseCasePort procesarPasoUseCase
    ) {
        this.iniciarSagaUseCase = iniciarSagaUseCase;
        this.consultarSagaUseCase = consultarSagaUseCase;
        this.procesarPasoUseCase = procesarPasoUseCase;
    }

    @PostMapping("/iniciar")
    public ResponseEntity<LiquidacionSagaResponseDTO> iniciarLiquidacion(@RequestBody IniciarLiquidacionCommand command) {
        LiquidacionSagaResponseDTO response = iniciarSagaUseCase.iniciarLiquidacion(command);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/{sagaId}")
    public ResponseEntity<LiquidacionSagaResponseDTO> consultarEstadoSaga(@PathVariable String sagaId) {
        LiquidacionSagaResponseDTO response = consultarSagaUseCase.consultarPorSagaId(sagaId);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/{sagaId}/simular-rollback")
    public ResponseEntity<Map<String, Object>> simularRollback(
            @PathVariable String sagaId,
            @RequestParam(defaultValue = "Prueba de compensación y rollback semántico en defensa") String motivo
    ) {
        procesarPasoUseCase.procesarFalloYCompensar(sagaId, motivo);
        return ResponseEntity.ok(Map.of(
                "status", "ROLLBACK_DISPARADO",
                "sagaId", sagaId,
                "motivo", motivo,
                "mensaje", "Se publicaron los comandos de compensación en Kafka hacia MS1 (PHP) y MS2 (NestJS)."
        ));
    }
}
