# 🧠 AegisCore AI — Memoria Histórica y Persistente

## 1. Identidad y Contexto del Proyecto
- **Nombre:** AegisCore AI (Sistema Distribuido ERP, Peritaje Inteligente y Liquidación Autónoma de Siniestros de Seguros).
- **Materia:** Ingeniería de Software II (2do Parcial) — Grupo #27.
- **Metodología:** ICONIX (BCE + Diagramas de Secuencia UML 2.5+ con métodos operacionales en Clases de Control).

## 2. Tecnologías y Arquitectura Base
- **Nivel 1 (Frontends + SSO):** Keycloak SSO (OAuth2 / OIDC PKCE RS256), Angular 17+ (ERP Admin & BI), React 18+ (PWA Offline / IA Local Web ONNX/TF.js), Flutter (App Móvil 100% Offline SQLite / IA Local TFLite).
- **Nivel 2 (4 Microservicios, 4 Lenguajes, 3 Arquitecturas):**
  - `ms1-polizas-php`: PHP 8.3 / Laravel bajo **Domain-Driven Design (DDD)** con GraphQL Federado y Facturación PDF `%PDF-1.4` con SHA-256.
  - `ms2-siniestros-nestjs`: TypeScript / NestJS 10 bajo **Clean Architecture + CQRS** con MongoDB y Push.
  - `ms3-actuarial-springboot`: Java 21 / Spring Boot 3 bajo **Arquitectura Hexagonal (Ports & Adapters)** con PostgreSQL y Orquestador Saga en Kafka.
  - `ms4-ia-mcp-python`: Python 3.11 / FastAPI con Scikit-Learn (Random Forest, K-Means, Isolation Forest), TensorFlow CNN, LangGraph y Servidor MCP con filtro OWASP Anti-SQLi.
- **Nivel 3 (Persistencia Políglota Cloud):** Neon PostgreSQL 16 (Relacional ACID), MongoDB Atlas 7 (Documental), Amazon DynamoDB (Clave-Valor `IdempotencyRecords`, `SesionesSSO`, `CacheCoberturaActiva`).
- **Nivel 4 (Orquestación y Automatización):** Apache Kafka (Event Broker / Saga Rollback), n8n (WhatsApp -> ERP -> Factura PDF / Siniestros Emergencia).

## 3. Estado de Hitos Completados
- **SP-01 a SP-04 (Infraestructura & Bases de Datos Cloud):** `docker-compose.yml` completo, `Neon PostgreSQL`, `MongoDB Atlas` y `Amazon DynamoDB Cloud` verificados y poblados.
- **Contratos Congelados:** `contracts/supergraph.graphql`, `contracts/saga-events.schema.json` e `contracts/idempotency-header.spec.json` intactos.
- **Perfil C (CU11 a CU15 — Completado):** MS4 Python IA + LangGraph + Servidor MCP Voz Anti-SQLi + MF1 Angular 17 BI + artefactos ICONIX/UML 2.5+.
- **Perfil B (CU06 a CU10 — Completado):** MS2 NestJS Clean/CQRS + MS3 Spring Boot Hexagonal/Saga + App Móvil Flutter Offline TFLite/SQLite + artefactos ICONIX/UML 2.5+.
- **Perfil A (CU01 a CU05 + Apoyo Saga CU09 y QR CU10 — Completado 28/10/2026):**
  - `backend/ms1-polizas-php`: 4 capas DDD en PHP 8.3, Supergraph GraphQL, OIDC+PKCE, Catálogo Planes y Coberturas con FK, Cotizador e Inserción de Pólizas, Webhook WhatsApp n8n, Generador PDF `%PDF-1.4` con SHA-256, Paso 2 Saga y Rollback. (`9 PASSED | 0 FAILED` en `tests/run_tests.php`).
  - `frontend/sso-shell-container` y `frontend/mf2-clientes-react`: Portal React 18 PWA Offline-First con `ValidadorNitidezLocalWebControl` (convolución Laplaciana 3x3 en navegador), pasarela QR idempotente y 5 vistas Boundary (`4 passed` en Vitest y build Vite de producción limpio).
  - `docs-iconix-uml/`: Especificación CU01–CU05, Diagramas de Robustez BCE, Diagramas de Secuencia UML 2.5+ y modelo XMI 2.1 (`aegiscore-perfil-a-iconix-uml25.xmi`).
