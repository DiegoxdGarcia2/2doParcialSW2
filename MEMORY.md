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

## 4. Hito de Seguridad SSO & RBAC Estricto ("Executive Precision" Multi-Rol)
- **Rediseño Humano Editorial de Alta Gama en Bóveda SSO (`frontend/sso-shell-container/src/index.html` - `:8080`):**
  - **Eliminación Total de Clichés de IA:** Se eliminaron gradientes neón (`bg-clip-text`), tarjetas genéricas de features técnicas irrelevantes (PKCE, DynamoDB, etc.), siglas técnicas en cabeceras y grillas de cajas saturadas.
  - **Diseño Editorial Split-Screen Asimétrico (Estilo Stripe / Mercury / Swiss Re):**
    - *Columna Izquierda (Lienzo blanco #FFFFFF):* Emblema sobrio de AegisCore, título editorial `Iniciar sesión`, inputs limpios y accesibles sin adornos innecesarios, checkbox sutil de persistencia, botón táctil `#005C55` "Continuar", y directorio compacto de perfiles demo con avatares neutros (`CM`, `MV`, `RP`, `AG`) y badges sobrios (`Cliente`, `Actuario`, `Perito`, `Admin`) con soporte de doble clic directo y un solo clic para autocompletar.
    - *Columna Derecha (Lienzo Arquitectónico #071C19):* Showcase visual de producto real con espécimen de póliza vehicular (`Toyota Hilux SRV 4x4 2025`, `$193,200.00`, prima `$720.00`, siniestralidad `42.8%`) y tarjeta superpuesta de liquidación aprobada (`#SIN-2026-089` por `$3,200.00`), con métricas operacionales auditadas en el pie.
  - **Vista `#workspace-hub`:** Solo visible tras login exitoso. Tarjetas con candado ("Acceso Restringido") para módulos no autorizados y visor de aplicaciones sincronizado.
- **Backend Autoritativo (`backend/ms1-polizas-php`):**
  - Sesión única global distribuida en DynamoDB (`ACTIVE_SSO_SESSION`). Nuevos logins invalidan sesiones previas con `SUPERSEDED_BY_NEW_LOGIN`.
  - Asignación estricta de roles por correo corporativo verificado en `AuthOIDCController`: `carlos.mendoza@gmail.com` (CLIENTE), `perito.campo@aegiscore.com` (PERITO), `actuario@aegiscore.com` (ACTUARIO) y `admin@aegiscore.com` (ADMIN).
  - Estado inicial limpio no autenticado (`authenticated: false`, `active_session: null`).
- **Guardias y Segregación RBAC en Frontends:**
  - `frontend/mf2-clientes-react` (`:3000`): Pantalla de bloqueo si no hay sesión activa; si `rol === 'CLIENTE'`, oculta selector de clientes (insignia fija) y pestaña catálogo, restringiendo simulación a administradores; botón directo "Cerrar Sesión".
  - `frontend/mf1-admin-angular` (`:4200`): Pantalla de bloqueo si no hay sesión activa; pantalla 403 para `CLIENTE`; menú lateral filtrado para `PERITO` (sólo CU11 y CU15) y `ACTUARIO` (excluye agente autónomo); botón directo "Cerrar Sesión".

## 5. Hito de Despliegue Multi-Cloud de Producción (10/11/2026)
- **Estrategia Tri-Cloud:** Despliegue autónomo en Google Cloud Run (MS1, MS4, MF1, n8n), Microsoft Azure Container Apps (Keycloak 24, MS3) y Amazon Web Services (MS2 en ECS Fargate, MF2 y SSO Shell en S3 HTTPS, DynamoDB, S3 Storage). Cero dependencia de servidores locales.
- **Persistencia Políglota Cloud:** Neon PostgreSQL 16 (Ohio, `aegiscore_erp`), MongoDB Atlas ReplicaSet (AWS, `aegiscore_siniestros_db`) y AWS DynamoDB (`AegisCore_IdempotencyRecords`, `SesionesSSO`).
- **Pruebas E2E de Producción:** 19/19 pruebas exitosas en `e2e_production_test_runner.py` cubriendo endpoints HTTP, queries GraphQL, eventos CQRS, ratios actuariales, visión artificial CrashNet, Random Forest y servidor MCP con filtro OWASP.
- **Estabilización de Frontends:**
  - Corrección de tipo MIME en Amazon S3 (`application/javascript`).
  - Migración a HTTPS oficial de Amazon S3 TLS para evadir bloqueos `net::ERR_BLOCKED_BY_CLIENT` de Brave Shields y Edge.
  - Inyección de `ChangeDetectorRef` en Angular 21 (zoneless) para resolver la congelación del estado `!authChecked`.
  - Contenerización y despliegue cloud de `automation-n8n` en Google Cloud Run.
  - Corrección de hoisting para `ocultarSpinnerVisor()` en el SSO Shell.
- **Documentación Centralizada:** Registrado en [`docs/DESPLIEGUE_MULTICLOUD_AEGISCORE.md`](file:///d:/Proyectos/2doParcialSW2/docs/DESPLIEGUE_MULTICLOUD_AEGISCORE.md) y sincronizado en la Bóveda Obsidian en `05 - Guias Operativas y Despliegue`.

