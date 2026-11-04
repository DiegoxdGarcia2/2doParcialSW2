# 🛡️ Casos de Uso CU06 al CU10 — Perfil B (Siniestros, Movilidad Offline & Saga)

Este documento detalla la especificación formal bajo metodología **ICONIX** y estándar **UML 2.5+** para los 5 casos de uso correspondientes a la **Célula B (Perfil B)** en **AegisCore AI**.

---

## 📑 Resumen de Casos de Uso (Perfil B)

| ID | Nombre | Componente Principal | Persistencia | Patrón Arquitectónico |
|---|---|---|---|---|
| **CU06** | Reportar Siniestro Vial de Emergencia SOS con Triaje | MS2 NestJS | MongoDB 7 (`2dsphere`) | Clean Architecture + CQRS |
| **CU07** | Inspeccionar Daños Offline en Terreno con Edge AI | Flutter Móvil | SQLite Local (`inspecciones.db`) | On-Device TFLite (LiteRT) |
| **CU08** | Sincronizar Expediente de Siniestro con Idempotencia | MS2 NestJS + Flutter | DynamoDB Local + MongoDB | `Idempotency-Key` UUIDv4 + SHA-256 |
| **CU09** | Liquidar y Pagar Indemnización (Patrón Saga en 3 MS) | MS3 Spring Boot | PostgreSQL + MongoDB + Kafka | Arquitectura Hexagonal + Saga Rollback |
| **CU10** | Procesar Cobro Recurrente de Primas y Pago QR Idempotente | MS3 Spring Boot | PostgreSQL + DynamoDB | Ports & Adapters + QR BCB/EMV |

---

## 🚨 CU06: Reportar Siniestro Vial SOS con Triaje
- **Objetivo:** Permite al asegurado emitir una alerta inmediata de colisión con captura automática de coordenadas GPS satelitales y fotos.
- **Triaje Automático:** Evalúa heridos, deformación estructural y despliegue de airbags mediante la regla de dominio puro `SeveridadVO.calcularTriaje()`.
- **Persistencia:** Guarda el expediente en MongoDB con GeoJSON `Point` indexado geoespacialmente con `2dsphere` para despacho de peritos por proximidad.

---

## 📱 CU07: Inspección Offline con IA Local (TFLite)
- **Objetivo:** Garantizar la operatividad del perito en zonas sin cobertura de internet (carreteras, estacionamientos subterráneos).
- **Edge AI On-Device:** Inferencia convolucional con el modelo cuantizado `damage_classifier.tflite` para parachoques, capó, faroles y puertas.
- **Persistencia Local:** Inserción transaccional atómica en SQLite local (`DatabaseHelper`) con hash criptográfico SHA-256 e Idempotency-Key UUIDv4.

---

## 🔄 CU08: Sincronización Idempotente con DynamoDB
- **Protocolo de Tolerancia a Fallas:** Basado en `contracts/idempotency-header.spec.json`.
- **Flujo:**
  1. `IdempotencyGuard` intercepta la petición `POST /api/v1/siniestros/peritaje/sync`.
  2. Adquiere lock `PROCESSING` en DynamoDB Local (`AegisCore_IdempotencyRecords`).
  3. Ejecuta `SincronizarPeritajeHandler` consolidando el reclamo en MongoDB en estado `PERITAJE_COMPLETADO`.
  4. Actualiza DynamoDB a `COMPLETED`.
  5. En cualquier reintento de red, DynamoDB responde en $< 5$ ms con `X-Cache-Lookup: HIT_IDEMPOTENCY_DYNAMODB` sin duplicar peritajes.

---

## ⚖️ CU09: Transacción Transversal Saga en 3 Microservicios
- **Orquestador:** `SagaLiquidacionOrchestratorService` en MS3 Spring Boot 3.
- **Paso 1 (MS2 NestJS):** `MarcarReclamoEnLiquidacionCommand` $\rightarrow$ Estado `EN_PROCESO_LIQUIDACION` en Mongo.
- **Paso 2 (MS1 PHP):** `DescontarCoberturaPolizaCommand` $\rightarrow$ Reducción de saldo en PostgreSQL.
- **Paso 3 (MS3 Spring Boot):** Verificación de reservas técnicas actuariales y desembolso contable.
- **Compensación Semántica (Rollback en Kafka):** Si en el Paso 3 falla la solvencia actuarial, MS3 publica en `aegiscore.saga.compensations`:
  1. `CompensarCoberturaCommand`: MS1 restituye la cobertura de la póliza.
  2. `RevertirEstadoReclamoCommand`: MS2 devuelve el siniestro a `PERITAJE_COMPLETADO`.

---

## 💳 CU10: Cobro Recurrente y Pago QR Idempotente
- **Arquitectura Hexagonal:** Puerto de entrada `ProcesarPagoPrimaQRUseCasePort`, adaptador JPA `PostgreSqlPagoPrimaAdapter` y adaptador `DynamoDbIdempotencyAdapter`.
- **Garantía Bancaria:** Generación y validación de códigos QR estándar con sellado idempotente para prevenir pagos duplicados por doble pulsación del cliente.
