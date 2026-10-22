# 🧠 AegisCore AI — Índice Principal (Map of Content)

Bienvenido a la Bóveda de Conocimiento Arquitectónico y Memoria Técnica de **AegisCore AI** (Sistema Distribuido ERP, Peritaje Inteligente y Liquidación Autónoma de Siniestros).

---

## 📌 Navegación Rápida
- [[02 - Arquitectura del Sistema/Arquitectura 4 Niveles y Patrones|🏛️ Arquitectura en 4 Niveles y Patrones de Código]]
- [[01 - Requisitos y Casos de Uso/Matriz de Casos de Uso CU01-CU15|📋 Requisitos y Casos de Uso (CU01 al CU15)]]
- [[03 - Modulos y Servicios Core/Microservicios y Modulos Backend|⚙️ Microservicios Backend y Frontends]]
- [[04 - Base de Datos y Modelos/Persistencia Poliglota y Esquemas|💾 Persistencia Políglota (PostgreSQL, MongoDB, DynamoDB)]]
- [[05 - Guias Operativas y Despliegue/Puesta en Marcha Docker Compose|🚀 Guía Operativa y Docker Compose]]
- [[06 - Bitacora y Memoria de Cambios (Changelog)/2026-10-22 - Inicializacion Scaffolding Fundacional|📝 Bitácora de Cambios (Changelog)]]

---

## 🎯 Resumen Ejecutivo del Ecosistema
- **Metodología:** ICONIX (BCE + Diagramas de Secuencia UML 2.5+).
- **Frontend Heterogéneo:** Angular 17+ (ERP Admin), React 18+ (PWA Offline / IA Local), Flutter (Móvil Offline SQLite / TFLite).
- **Autenticación Única:** Keycloak SSO (OAuth2 / OIDC con JWT RS256).
- **Backend Políglota:**
  - MS1: PHP 8.3 / Laravel (DDD + GraphQL).
  - MS2: TypeScript / NestJS 10 (Clean Architecture + CQRS).
  - MS3: Java 21 / Spring Boot 3 (Arquitectura Hexagonal + Orquestador Saga).
  - MS4: Python 3.11 / FastAPI (ML Random Forest, K-Means, Isolation Forest, TensorFlow CNN, LangGraph, Servidor MCP con blindaje Anti-SQLi).
- **Persistencia Políglota:** PostgreSQL 16 (ACID), MongoDB 7 (Documental), DynamoDB Local (Clave-Valor Idempotencia).
- **Orquestación y Automatización:** Apache Kafka (Saga Rollback) y n8n (WhatsApp / Facturación PDF).
