# 🤖 Guía para Agentes de Inteligencia Artificial — AegisCore AI

Este archivo sirve como punto de referencia universal para asistentes y agentes de IA (Cursor, Windsurf, Gemini, Claude, Copilot, etc.) que trabajen en este repositorio.

---

## 🧭 Contexto Rápido del Proyecto
- **Nombre:** AegisCore AI — ERP Distribuido, Peritaje Inteligente y Liquidación Autónoma de Siniestros.
- **Metodología:** **ICONIX** con trazabilidad a objetos Boundary, Control y Entity.
- **Diagramas de Secuencia:** Estándar **UML 2.5+**, especificando los métodos en la Clase de Control.
- **División del Equipo (3 Integrantes):**
  - **Perfil A (CU01 a CU05):** Keycloak SSO + React PWA (IA Local Web) + MS1 PHP (DDD + GraphQL) + n8n.
  - **Perfil B (CU06 a CU10):** Flutter (Offline SQLite + TFLite) + MS2 NestJS (Clean + CQRS) + MS3 Spring Boot (Hexagonal + Saga) + DynamoDB.
  - **Perfil C (CU11 a CU15):** MS4 Python (Random Forest, K-Means, Isolation Forest, TensorFlow CNN, LangGraph, Servidor MCP Voz Anti-SQLi) + Angular BI.

---

## 🏛️ Patrones de Código por Microservicio
1. `backend/ms1-polizas-php`: **Domain-Driven Design (DDD)** táctico y estratégico.
2. `backend/ms2-siniestros-nestjs`: **Clean Architecture + CQRS** (use-cases divididos en commands y queries).
3. `backend/ms3-actuarial-springboot`: **Arquitectura Hexagonal (Ports & Adapters)**.
4. `backend/ms4-ia-mcp-python`: **Pipelines de IA + Servidor MCP** con filtro OWASP.

---

## 🔒 Contratos Congelados (`contracts/`)
**REGLA ESTRICTA:** Los contratos en `contracts/supergraph.graphql`, `contracts/saga-events.schema.json` e `contracts/idempotency-header.spec.json` son la fuente de verdad inmutable entre los 3 integrantes. No los alteres sin previo consenso del equipo.

---

## 💾 Persistencia Políglota
- **PostgreSQL 16:** Datos ACID relacionales en `aegiscore_erp` (incluye 1,200 registros sintéticos para Random Forest).
- **MongoDB 7:** Expedientes no estructurados en `aegiscore_siniestros` con índice `2dsphere`.
- **Amazon DynamoDB Local:** Tabla `IdempotencyRecords` para control de duplicados con pésima señal.

## 🎨 Sistema de Diseño Oficial y Google Stitch MCP
- **Tema Oficial:** **"Executive Precision"** (Extraído de Google Stitch MCP `projects/9132956203380267795`).
- **Paleta de Colores:** Executive Teal (`#005C55`, `#0F766E`), Deep Navy (`#0F172A`), AI & Telemetry Royal Indigo (`#4F46E5`, `#3F33D6`), Base Alabaster (`#F8FAFC`).
- **Tipografías:** Plus Jakarta Sans (Headlines), Inter (Forms & Body), JetBrains Mono (Telemetría, VIN, Pólizas, Monospace).
- **Recursos Disponibles:**
  - `frontend/design-system/DESIGN_SYSTEM.md`: Guía de estilos y trazabilidad ICONIX.
  - `frontend/design-system/variables.css`: Variables CSS nativas para React, Angular y Flutter.
  - `frontend/design-system/tokens.json`: Tokens W3C JSON estructurados.
  - `frontend/design-system/tailwind.preset.js`: Preset compartido para Tailwind.
  - `frontend/design-system/screens/`: 6 pantallas oficiales extraídas (`ai-damage-inspector.html`, `risk-fraud-sentinel.html`, `autonomous-agent-monitor.html`, `executive-kpi-dashboard.html`, `actuarial-sales-prediction.html`, `deep-learning-damage-assessment.html`).
  - Visor interactivo: `frontend/design-system/screens/index.html`.

---

## 🚀 Comandos Esenciales
- Arrancar todo: `docker compose up -d`
- Ver estado: `docker compose ps`
- Ver logs: `docker compose logs -f <servicio>`
- Reglas detalladas: Ver [`.agents/rules/aegiscore-architecture-rules.md`](file:///.agents/rules/aegiscore-architecture-rules.md)

