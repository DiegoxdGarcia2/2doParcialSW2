# 🛡️ MS2 NestJS: Siniestros, Triaje & Idempotencia (Clean Architecture + CQRS)

## 📌 Contexto
- **Directorio:** `backend/ms2-siniestros-nestjs/`
- **Framework:** TypeScript / NestJS 10
- **Puerto:** `8002`
- **Patrón:** Clean Architecture + CQRS (Command Query Responsibility Segregation)
- **Persistencia:** MongoDB 7 (Expedientes con índice geoespacial `2dsphere`) y Amazon DynamoDB Local (`AegisCore_IdempotencyRecords`).

---

## 🏛️ Estructura de Capas
1. **Domain (`src/domain/`):**
   - Agregado: `ReclamoSiniestro` (gestiona ciclo de vida, historial de transiciones y cálculo de deducibles).
   - Entidad: `PeritajeDetalle` (partes impactadas, fotos y hash de integridad offline).
   - Value Objects: `SeveridadVO` (triaje estricto), `UbicacionGeoVO` (coordenadas GPS `Point`), `EstadoReclamoVO`.
   - Repositorios: `IReclamoRepository`, `IIdempotencyRepository`.
2. **Application (`src/application/`):**
   - **Commands:** `RegistrarSiniestroCommand`, `SincronizarPeritajeCommand`, `AsignarPeritoCommand`, `MarcarEnLiquidacionCommand`, `RevertirEstadoReclamoCommand`.
   - **Queries:** `ObtenerSiniestroPorIdQuery`, `ListarPorClienteQuery`, `ListarSiniestrosCercanosGeoQuery`.
3. **Infrastructure (`src/infrastructure/`):**
   - Persistencia: `MongoReclamoRepository` con Mongoose Schema `expedientes_siniestros`.
   - Idempotencia: `IdempotencyGuard` y `DynamoIdempotencyRepository` con `@aws-sdk/lib-dynamodb`.
   - Mensajería: `KafkaSagaConsumerService` y `KafkaEventPublisherAdapter` para eventos y compensaciones Saga.
4. **Presentation (`src/presentation/`):**
   - `SiniestrosCommandController`: Rutas `/api/v1/siniestros/sos`, `/api/v1/siniestros/peritaje/sync`.
   - `SiniestrosQueryController`: Búsquedas por ID, cliente y geoproximidad GPS.
   - `HealthController`: Chequeo de salud UP en `/health`.

