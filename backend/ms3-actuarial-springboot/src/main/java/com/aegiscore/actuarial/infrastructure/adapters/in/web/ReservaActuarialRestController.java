package com.aegiscore.actuarial.infrastructure.adapters.in.web;

import com.aegiscore.actuarial.application.ports.out.ReservaTecnicaRepositoryPort;
import com.aegiscore.actuarial.domain.model.reserva.ReservaTecnica;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/v1/actuarial/reserva")
@CrossOrigin(origins = "*")
public class ReservaActuarialRestController {

    private final ReservaTecnicaRepositoryPort reservaRepository;

    public ReservaActuarialRestController(ReservaTecnicaRepositoryPort reservaRepository) {
        this.reservaRepository = reservaRepository;
    }

    @GetMapping
    public ResponseEntity<Map<String, Object>> obtenerReservaVigente() {
        Optional<ReservaTecnica> reservaOpt = reservaRepository.obtenerReservaActual();
        if (reservaOpt.isPresent()) {
            ReservaTecnica r = reservaOpt.get();
            return ResponseEntity.ok(Map.of(
                    "periodo", r.getPeriodo(),
                    "saldoFondoReserva", r.getSaldoFondoReserva(),
                    "limiteSolvenciaMinimo", r.getLimiteSolvenciaMinimo(),
                    "siniestrosLiquidadosAcumulado", r.getSiniestrosLiquidadosAcumulado(),
                    "alertasLiquidez", r.isAlertasLiquidez(),
                    "estadoSolvencia", r.isAlertasLiquidez() ? "ALERTA_RIESGO" : "OPTIMO"
            ));
        }
        return ResponseEntity.notFound().build();
    }
}
