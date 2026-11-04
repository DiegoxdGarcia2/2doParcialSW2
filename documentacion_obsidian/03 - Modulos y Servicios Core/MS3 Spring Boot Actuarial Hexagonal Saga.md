# ☕ MS3 Spring Boot 3: Motor Actuarial, Cobranzas & Orquestador Saga (Arquitectura Hexagonal)

## 📌 Contexto
- **Directorio:** `backend/ms3-actuarial-springboot/`
- **Framework:** Java 21 / Spring Boot 3.2.x
- **Puerto:** `8003`
- **Patrón:** Arquitectura Hexagonal (Ports & Adapters)
- **Persistencia:** PostgreSQL 16 (`orden_liquidacion_saga`, `pago_prima`, `reserva_tecnica`) y DynamoDB Local.
- **Event Broker:** Apache Kafka (Orquestador Saga).

---

## 🏛️ Estructura Hexagonal
1. **Dominio Puro (`domain/`):**
   - Entidades: `OrdenLiquidacion`, `SagaInstance`, `PagoPrima`, `ReservaTecnica`.
   - Servicios de Dominio: `CalculoActuarialService` (reglas actuariales, primas puras y validación de solvencia técnica).
2. **Puertos de Entrada / Inbound (`application/ports/in/`):**
   - `LiquidarSiniestroSagaUseCasePort`
   - `ProcesarPagoPrimaQRUseCasePort`
   - `CompensarSagaLiquidacionUseCasePort`
3. **Puertos de Salida / Outbound (`application/ports/out/`):**
   - `OrdenLiquidacionRepositoryPort`
   - `PagoPrimaRepositoryPort`
   - `SagaEventPublisherPort`
   - `IdempotencyLockPort`
4. **Adaptadores de Entrada (`infrastructure/adapters/in/`):**
   - REST Controllers: `LiquidacionRestController`, `PagoQRRestController`, `SagaStatusRestController`.
   - Kafka Listeners: Consumo de eventos Saga de MS2 y MS1.
5. **Adaptadores de Salida (`infrastructure/adapters/out/`):**
   - JPA PostgreSQL: Adaptadores Spring Data JPA.
   - Kafka Producer: Despacho a `aegiscore.saga.commands` y `aegiscore.saga.compensations`.
   - DynamoDB Adapter: Candados de idempotencia para cobro QR.

