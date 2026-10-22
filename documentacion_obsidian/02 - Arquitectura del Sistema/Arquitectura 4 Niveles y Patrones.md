# 🏛️ Arquitectura del Sistema en 4 Niveles y Patrones de Código

## 1. Nivel 1: Micro-Frontends e Identidad Única
- **Keycloak SSO:** OAuth2/OIDC con tokens JWT RS256. Centraliza la autenticación (CU01).
- **Angular 17+:** Panel administrativo pesado, dashboard estadístico nativo con KPIs en código y visor de voz MCP.
- **React 18+ PWA:** Portal cliente para cotización y contratación con GraphQL e inferencia local web (`TensorFlow.js` / `ONNX Web`).
- **Flutter:** App móvil de peritos en campo que funciona 100% offline con SQLite y agente local `TensorFlow Lite`.

## 2. Nivel 2: Microservicios Backend y Patrones Obligatorios
- **`backend/ms1-polizas-php`:** 
  - **Patrón:** **Domain-Driven Design (DDD)** táctico y estratégico (`Domain/`, `Application/`, `Infrastructure/`, `Presentation/GraphQL/`).
  - **Responsabilidad:** Pólizas, clientes, coberturas y facturación.
- **`backend/ms2-siniestros-nestjs`:**
  - **Patrón:** **Clean Architecture + CQRS** (`domain/`, `application/use-cases/commands` y `queries/`, `infrastructure/`, `presentation/`).
  - **Responsabilidad:** Expedientes multimedia, triaje y notificaciones push.
- **`backend/ms3-actuarial-springboot`:**
  - **Patrón:** **Arquitectura Hexagonal (Ports & Adapters)** (`domain/`, `application/ports/in/` y `out/`, `infrastructure/adapters/in/` y `out/`).
  - **Responsabilidad:** Cálculo actuarial, cobros QR idempotentes y Orquestador del Patrón Saga.
- **`backend/ms4-ia-mcp-python`:**
  - **Responsabilidad:** ML Supervisado (Random Forest), No Supervisado (K-Means, Isolation Forest), Deep Learning (TensorFlow CNN), Agente LangGraph y Servidor MCP con filtro OWASP Anti-SQLi.

## 3. Nivel 3: Persistencia Políglota
- **PostgreSQL 16:** Datos ACID relacionales de clientes, pólizas, facturas y liquidación.
- **MongoDB 7:** Expedientes no estructurados, evidencias multimedia y logs de IA.
- **DynamoDB Local:** Control de idempotencia (`IdempotencyRecords`) y sesiones rápidas.

## 4. Nivel 4: Gateway, Orquestación Saga y n8n
- **Apache Kafka:** Transacción transversal en 3 microservicios (CU09) con rollback compensatorio.
- **n8n:** Flujos multicanal WhatsApp -> ERP -> Factura PDF y Triaje de Siniestros.
