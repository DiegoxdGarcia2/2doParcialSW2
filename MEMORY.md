# 🧠 AegisCore AI — Memoria Histórica y Persistente

## 1. Identidad y Contexto del Proyecto
- **Nombre:** AegisCore AI (Sistema Distribuido ERP, Peritaje Inteligente y Liquidación Autónoma de Siniestros de Seguros).
- **Materia:** Ingeniería de Software II (2do Parcial) — Grupo #27.
- **Metodología:** ICONIX (BCE + Diagramas de Secuencia UML 2.5+ con métodos operacionales en Clases de Control).

## 2. Tecnologías y Arquitectura Base
- **Nivel 1 (Frontends + SSO):** Keycloak SSO (OAuth2 / OIDC RS256), Angular 17+ (ERP Admin & BI), React 18+ (PWA Offline / IA Local Web ONNX/TF.js), Flutter (App Móvil 100% Offline SQLite / IA Local TFLite).
- **Nivel 2 (4 Microservicios, 4 Lenguajes, 3 Arquitecturas):**
  - `ms1-polizas-php`: PHP 8.3 / Laravel bajo **Domain-Driven Design (DDD)** con GraphQL.
  - `ms2-siniestros-nestjs`: TypeScript / NestJS 10 bajo **Clean Architecture + CQRS** con MongoDB y Push.
  - `ms3-actuarial-springboot`: Java 21 / Spring Boot 3 bajo **Arquitectura Hexagonal (Ports & Adapters)** con PostgreSQL y Orquestador Saga en Kafka.
  - `ms4-ia-mcp-python`: Python 3.11 / FastAPI con Scikit-Learn (Random Forest, K-Means, Isolation Forest), TensorFlow CNN, LangGraph y Servidor MCP con filtro OWASP Anti-SQLi.
- **Nivel 3 (Persistencia Políglota):** PostgreSQL 16 (Relacional ACID), MongoDB 7 (Documental), DynamoDB Local (Clave-Valor IdempotencyRecords UUIDv4).
- **Nivel 4 (Orquestación y Automatización):** Apache Kafka (Event Broker / Saga Rollback), n8n (WhatsApp -> ERP -> Factura PDF / Siniestros Emergencia).

## 3. Estado de Hitos Completados (22 de Octubre de 2026)
- **SP-01 (Scaffolding):** Scripts `setup-workspace.ps1` y `setup-workspace.sh` ejecutados con 145 directorios creados.
- **SP-01 (Docker Compose):** `docker-compose.yml` completo orquestando 10 servicios con redes, volúmenes y healthchecks.
- **SP-03 (PostgreSQL):** `infra/db-init/postgres-init.sql` con tablas ACID y 1,200 registros sintéticos para Random Forest.
- **SP-04 (MongoDB & DynamoDB):** `infra/db-init/mongo-init.js` con esquemas JSON e índices 2dsphere; `dynamodb-init.sh` y `.ps1` para IdempotencyRecords.
- **Contratos Congelados:** `contracts/supergraph.graphql`, `contracts/saga-events.schema.json` e `contracts/idempotency-header.spec.json`.
- **SSO & n8n:** Realm `infra/keycloak-sso/aegiscore-realm.json` y workflows CU05 y CU06 en `automation-n8n/`.
