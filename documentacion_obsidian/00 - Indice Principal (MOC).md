# 🧠 AegisCore AI — Índice Principal (Map of Content)

Bienvenido a la Bóveda de Conocimiento Arquitectónico y Memoria Técnica de **AegisCore AI** (Sistema Distribuido ERP, Peritaje Inteligente y Liquidación Autónoma de Siniestros).

---

## 📌 Navegación Rápida
- [[02 - Arquitectura del Sistema/Arquitectura 4 Niveles y Patrones|🏛️ Arquitectura en 4 Niveles y Patrones de Código]]
- [[01 - Requisitos y Casos de Uso/CU01 al CU05 - Comercial, SSO, React PWA y n8n|🛡️ Perfil A: Casos de Uso CU01 al CU05 (SSO, GraphQL, DDD, React PWA, n8n)]]
- [[01 - Requisitos y Casos de Uso/CU06 al CU10 - Siniestros, Movil Offline, Idempotencia y Transaccion Saga|🛡️ Perfil B: Casos de Uso CU06 al CU10 (Siniestros, Offline, Saga)]]
- [[01 - Requisitos y Casos de Uso/CU11 al CU15 - Inteligencia Artificial, Agentes y Servidor MCP|🧠 Perfil C: Casos de Uso CU11 al CU15 (IA, Agentes, MCP)]]
- [[03 - Modulos y Servicios Core/MS1 PHP Laravel DDD y MF2 React PWA|🐘 MS1 PHP 8.3 (DDD + GraphQL) & ⚛️ MF2 React 18 PWA]]
- [[03 - Modulos y Servicios Core/MS2 NestJS Siniestros CQRS|🛡️ MS2 NestJS (Clean Arch + CQRS)]]
- [[03 - Modulos y Servicios Core/MS3 Spring Boot Actuarial Hexagonal Saga|☕ MS3 Spring Boot (Hexagonal + Saga)]]
- [[03 - Modulos y Servicios Core/App Peritos Flutter Offline TFLite|📱 App Móvil Flutter (Offline SQLite + TFLite)]]
- [[03 - Modulos y Servicios Core/MS4 Python IA y Servidor MCP|🐍 MS4 Python (IA, LangGraph & Servidor MCP)]]
- [[03 - Modulos y Servicios Core/MF1 Angular Admin y Dashboard BI|🅰️ MF1 Angular Admin & BI Actuarial]]
- [[04 - Base de Datos y Modelos/Persistencia Poliglota y Esquemas|💾 Persistencia Políglota (PostgreSQL, MongoDB, DynamoDB)]]
- [[05 - Guias Operativas y Despliegue/Puesta en Marcha Docker Compose|🚀 Guía Operativa y Docker Compose]]
- [[06 - Bitacora y Memoria de Cambios (Changelog)/2026-10-28 - Implementacion Completa Casos de Uso Perfil A (CU01-CU05)|📝 Bitácora: Cierre Completo Perfil A (CU01-CU05)]]
- [[06 - Bitacora y Memoria de Cambios (Changelog)/2026-10-27 - Implementacion Completa Casos de Uso Perfil B (CU06-CU10)|📝 Bitácora: Cierre Completo Perfil B (CU06-CU10)]]
- [[06 - Bitacora y Memoria de Cambios (Changelog)/2026-10-27 - Implementacion Completa Casos de Uso Perfil C (CU11-CU15)|📝 Bitácora: Cierre Completo Perfil C (CU11-CU15)]]

---

## 🎯 Resumen Ejecutivo del Ecosistema
- **Metodología:** ICONIX (BCE + Diagramas de Secuencia UML 2.5+).
- **Frontend Heterogéneo:** Angular 17+ (ERP Admin), React 18+ (PWA Offline / IA Local), Flutter (Móvil Offline SQLite / TFLite).
- **Autenticación Única:** Keycloak SSO (OAuth2 / OIDC con PKCE S256 y JWT RS256).
- **Backend Políglota:**
  - MS1: PHP 8.3 / Laravel (DDD + GraphQL Federado + Facturación PDF SHA-256).
  - MS2: TypeScript / NestJS 10 (Clean Architecture + CQRS).
  - MS3: Java 21 / Spring Boot 3 (Arquitectura Hexagonal + Orquestador Saga).
  - MS4: Python 3.11 / FastAPI (ML Random Forest, K-Means, Isolation Forest, TensorFlow CNN, LangGraph, Servidor MCP con blindaje Anti-SQLi).
- **Persistencia Políglota Cloud:** Neon PostgreSQL 16 (ACID), MongoDB Atlas 7 (Documental), Amazon DynamoDB (Clave-Valor Idempotencia y Sesiones SSO).
- **Orquestación y Automatización:** Apache Kafka (Saga Rollback) y n8n (WhatsApp -> ERP -> Factura PDF / Siniestros Emergencia).
