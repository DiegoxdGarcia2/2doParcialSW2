---
trigger: always_on
description: Reglas arquitectonicas, metodologia ICONIX, division de perfiles y directrices para agentes IA en AegisCore AI.
---

# 🛡️ Reglas y Contexto Arquitectónico Global — AegisCore AI

Este documento rige el comportamiento de cualquier agente de inteligencia artificial (o desarrollador) que colabore en el proyecto **"AegisCore AI"** (Sistema Distribuido de Gestión Empresarial ERP, Peritaje Inteligente y Liquidación Autónoma de Siniestros de Seguros — 2do Parcial SW2, Grupo #27).

---

## 1. Metodología Obligatoria: ICONIX + UML 2.5+
Cualquier propuesta técnica, refactorización o diseño debe mantener trazabilidad ICONIX:
1. **Objetos Boundary (Vista / Interfaz):** Formularios web, vistas móviles, bot WhatsApp o comandos de voz.
2. **Objetos Control (Lógica de Aplicación / Orquestación):** Servicios de aplicación, casos de uso, controladores o adaptadores de entrada. **En los Diagramas de Secuencia UML 2.5+, los métodos operacionales deben pertenecer explícitamente a la clase de control.**
3. **Objetos Entity (Persistencia):** Tablas PostgreSQL, colecciones MongoDB o registros DynamoDB.

---

## 2. División de Responsabilidades (3 Integrantes / Células)
Para no bloquear el desarrollo, cada integrante es dueño de su célula vertical basada en **Contratos Congelados** (`contracts/`):

### 🅰️ Perfil A (Comercial, SSO, Web React & n8n)
- **Casos de Uso:** `CU01` (SSO Keycloak), `CU02` (Estado Unificado GraphQL), `CU03` (Catálogo Planes y Clientes), `CU04` (Cotización Web con IA Local ONNX/TF.js), `CU05` (Pedidos WhatsApp $\rightarrow$ Factura PDF con n8n).
- **Componentes:**
  - Micro-Frontend React 18+ PWA (`frontend/mf2-clientes-react`).
  - Keycloak SSO (`infra/keycloak-sso/`).
  - Microservicio 1 PHP 8.3 / Laravel bajo **Domain-Driven Design (DDD)** (`backend/ms1-polizas-php/`).
  - PostgreSQL (Esquema Comercial).
  - Flujo n8n (`automation-n8n/workflow-pedido-poliza-whatsapp-factura.json`).

### 🅱️ Perfil B (Siniestros, Móvil Offline, Idempotencia & Saga)
- **Casos de Uso:** `CU06` (Siniestro Emergencia WhatsApp + Triaje), `CU07` (Inspección Móvil Offline SQLite + TFLite), `CU08` (Sincronización Idempotente con DynamoDB), `CU09` (Liquidación Transversal Saga en 3 MS), `CU10` (Cobros QR Idempotentes).
- **Componentes:**
  - Microservicio 2 NestJS 10 bajo **Clean Architecture + CQRS** (`backend/ms2-siniestros-nestjs/`).
  - Microservicio 3 Java 21 / Spring Boot 3 bajo **Arquitectura Hexagonal** (`backend/ms3-actuarial-springboot/`).
  - App Móvil Flutter (`frontend/app-peritos-flutter/`).
  - MongoDB 7 (Expedientes) y Amazon DynamoDB Local (`IdempotencyRecords`).
  - Apache Kafka (Bus de eventos Saga y Compensaciones).

### 🅲 Perfil C (IA, Deep Learning TensorFlow, Agentes, MCP & Angular BI)
- **Casos de Uso:** `CU11` (Visión Artificial Choques con TensorFlow CNN), `CU12` (Predicción Ventas y Primas con Random Forest), `CU13` (Segmentación K-Means y Detección Fraude Isolation Forest), `CU14` (Monitoreo con Agente LangGraph Metas y Skills), `CU15` (Reportes por Voz con Servidor MCP y blindaje Anti-SQLi).
- **Componentes:**
  - Microservicio 4 Python 3.11 / FastAPI (`backend/ms4-ia-mcp-python/`).
  - Modelos Scikit-Learn y TensorFlow / Keras.
  - Servidor con Protocolo MCP (`Model Context Protocol`) y Whisper STT.
  - Micro-Frontend Angular 17+ (`frontend/mf1-admin-angular/`) con Dashboards nativos en código (Chart.js / ECharts, **sin Power BI**).

---

## 3. Patrones de Arquitectura de Código Obligatorios

| Microservicio | Lenguaje / Framework | Patrón de Arquitectura | Regla de Implementación |
|---|---|---|---|
| **`ms1-polizas-php`** | PHP 8.3 / Laravel | **Domain-Driven Design (DDD)** | Separar estrictamente `Domain/` (Agregados, Entidades, VO, Repositorios), `Application/` (Commands/Queries/DTOs) e `Infrastructure/` (Eloquent, Kafka, DynamoDB). |
| **`ms2-siniestros-nestjs`** | TypeScript / NestJS 10 | **Clean Architecture + CQRS** | Separar casos de uso en `commands/` y `queries/`. El dominio no debe depender de Mongoose ni de ningún framework externo. |
| **`ms3-actuarial-springboot`** | Java 21 / Spring Boot 3 | **Arquitectura Hexagonal (Ports & Adapters)** | `domain/` aislado; `application/ports/in/` y `ports/out/`; `infrastructure/adapters/in/` (REST/Kafka) y `adapters/out/` (JPA/DynamoDB/Kafka). |
| **`ms4-ia-mcp-python`** | Python 3.11 / FastAPI | **Pipelines de IA + Servidor MCP** | Los modelos de ML/DL corren en módulos aislados. El Servidor MCP solo expone Tools tipadas con JSON Schema. |

---

## 4. Persistencia Políglota y Reglas de Integración

1. **PostgreSQL 16 (`aegiscore_erp`):** Usada por MS1 y MS3 para datos transaccionales ACID (Pólizas, Clientes, Facturas, Pagos QR, Liquidaciones). Incluye tabla `dataset_historico_ml_polizas` con 1,200 registros sintéticos.
2. **MongoDB 7 (`aegiscore_siniestros`):** Usada por MS2 y MS4 para expedientes semi-estructurados, peritajes fotográficos e índice geoespacial `2dsphere`.
3. **Amazon DynamoDB Local:** Tabla `IdempotencyRecords` (`idempotency_key` UUIDv4 + Hash SHA-256) para evitar duplicación ante intermitencia de red (latencia $< 5$ ms).

---

## 5. Regla de Oro: Contratos Congelados
- **NUNCA** modificar unilateralmente los archivos dentro de `contracts/`:
  - `contracts/supergraph.graphql`
  - `contracts/saga-events.schema.json`
  - `contracts/idempotency-header.spec.json`
- Cualquier cambio de contrato requiere acuerdo unánime de los 3 integrantes.
- Si se añade un campo nuevo a un microservicio, debe mapearse a las estructuras ya acordadas en estos contratos.

---

## 6. Seguridad OWASP en el Servidor MCP (CU15)
- El usuario puede solicitar reportes mediante lenguaje natural dictado por micrófono (Whisper STT).
- **Prohibido concatenar texto dictado a consultas SQL dinámicas.**
- El audio transcrito pasa por un filtro de sanitización OWASP. El agente solo puede invocar **Tools MCP tipadas** predefinidas que ejecutan consultas mediante **ORMs parametrizados**.
