# 🛡️ CU01 al CU05 — Comercial, SSO, React PWA y Automatización n8n (Perfil A)

## 1. Alcance Funcional del Perfil A (42 Puntos / 26 Horas)
El **Perfil A** constituye el núcleo comercial, de identidad federada y de experiencia del asegurado de **AegisCore AI**:
- **CU01:** Inicio de Sesión Único Multi-Aplicación (SSO) con Keycloak 24 (OAuth 2.0 / OIDC + PKCE `S256` + JWT `RS256`) y registro de sesión unificada en Amazon DynamoDB (`SesionesSSO`).
- **CU02:** Consulta de Estado Unificado del Asegurado en una sola petición GraphQL (`resumenUnificadoAsegurado`), federando Neon PostgreSQL 16 (Pólizas y Coberturas), MongoDB Atlas 7 (Expedientes de Siniestros) y Amazon DynamoDB (`CacheCoberturaActiva`).
- **CU03:** Gestión del Catálogo de Planes de Seguro (`PlanSeguro`), Coberturas con llave foránea (`Cobertura`, FK `plan_id`) y Clientes Asegurados (`Cliente`) bajo **Domain-Driven Design (DDD)** táctico y estratégico en PHP 8.3.
- **CU04:** Cotización y Emisión de Póliza en Línea con Validación de Documentos por IA Local en Navegador (`ValidadorNitidezLocalWebControl`, kernel convolucional Laplaciano $3 \times 3$, umbral $\ge 0.65$) y cola de sincronización Offline PWA con `Idempotency-Key` (UUIDv4).
- **CU05:** Contratación o Renovación de Póliza por WhatsApp y Emisión Automática de Factura Fiscal / Nota de Venta en PDF (`%PDF-1.4`) con sello digital `SHA-256` orquestado con **n8n**.
- **Apoyo CU09 & CU10:** Ejecución del Paso 2 de la Saga (`descontarTechoAnualPoliza()`) y su compensación por Rollback (`compensarCoberturaSaga()`) en MS1 PHP, más la Pasarela de Pago de Prima por QR Idempotente en React 18 PWA.

---

## 2. Trazabilidad Metodológica ICONIX + UML 2.5+
| Caso de Uso | Objeto Boundary (Vista) | Objeto Control (Métodos UML 2.5+) | Objeto Entity (Persistencia) |
|---|---|---|---|
| **CU01** | `LoginUnificadoSSOView` | `AuthOIDCController`: `autenticarUsuarioOIDC()`, `validarTokenJwtRS256()`, `registrarSesionUnificadaDynamoDB()` | `UsuarioRol` (PG), `SesionUnificadaToken` (DynamoDB) |
| **CU02** | `ResumenCoberturaClienteView` | `ApolloFederationResolver`: `resolverResumenUnificadoAsegurado()`, `federarExpedientesSiniestrosMongoDB()` | `Poliza` (PG), `ExpedienteSiniestro` (Mongo), `CacheCoberturaActiva` (DynamoDB) |
| **CU03** | `GestionCatalogoSegurosView` | `CatalogoPolizaApplicationService`: `listarPlanesSeguro()`, `registrarPlanSeguroDDD()`, `agregarCoberturaAPlan()`, `registrarClienteDDD()` | `PlanSeguro`, `Cobertura` (FK), `Cliente` (PG) |
| **CU04** | `CotizadorInscripcionWebView` | `ValidadorNitidezLocalWebControl`: `validarNitidez()`; `EmisionPolizaGraphQLController`: `cotizarPolizaEnLinea()`, `insertarPoliza()` | `Poliza`, `BienAseguradoVehiculo` (PG) |
| **CU05** | `BotConversacionalWhatsAppPoliza` | `WebhookTriggerN8N`, `RecepcionPedidoService`: `procesarPedidoPolizaWhatsApp()`, `FacturacionService`: `generarFacturaNotaVentaPDF()` | `Poliza`, `FacturaNotaVenta` (PG) |
| **CU09 (MS1)** | Kafka Consumer / REST Saga | `PolizaCoberturaService`: `descontarTechoAnualPoliza()`, `compensarCoberturaSaga()` | `Poliza` (PG) |

---

## 3. Enlaces Relacionados
- [[00 - Indice Principal (MOC)]]
- [[03 - Modulos y Servicios Core/MS1 PHP Laravel DDD y MF2 React PWA]]
- [[06 - Bitacora y Memoria de Cambios (Changelog)/2026-10-28 - Implementacion Completa Casos de Uso Perfil A (CU01-CU05)]]

