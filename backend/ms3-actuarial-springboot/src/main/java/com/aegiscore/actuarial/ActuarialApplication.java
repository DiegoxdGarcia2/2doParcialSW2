package com.aegiscore.actuarial;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.Map;

@SpringBootApplication
@RestController
public class ActuarialApplication {

    public static void main(String[] args) {
        SpringApplication.run(ActuarialApplication.java, args);
    }

    @GetMapping("/health")
    public Map<String, Object> health() {
        return Map.of(
            "status", "UP",
            "service", "ms3-actuarial-springboot",
            "pattern", "Arquitectura Hexagonal (Ports & Adapters)",
            "role", "Motor Actuarial y Orquestador Saga",
            "javaVersion", System.getProperty("java.version"),
            "timestamp", Instant.now().toString()
        );
    }

    @GetMapping("/api/actuarial/saga-status")
    public Map<String, Object> sagaStatus() {
        return Map.of(
            "orchestrator", "SagaLiquidacionOrchestrator",
            "supportedSagas", new String[]{"CU09: Liquidación y Pago de Indemnización de Siniestro"},
            "steps", new String[]{
                "1. MS2 NestJS -> MarcarReclamoEnLiquidacion",
                "2. MS1 PHP Laravel -> DescontarCoberturaPoliza",
                "3. MS3 Spring Boot -> AprobarDesembolsoLiquidacion"
            },
            "compensationFlow", "Kafka aegiscore.saga.compensations"
        );
    }
}
