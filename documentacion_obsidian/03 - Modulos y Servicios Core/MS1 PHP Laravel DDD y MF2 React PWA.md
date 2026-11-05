# 🐘 MS1 PHP 8.3 (DDD + GraphQL) & ⚛️ MF2 React 18 PWA (IA Local Web)

## 1. Arquitectura de `backend/ms1-polizas-php` (Domain-Driven Design)
El Microservicio 1 implementa estrictamente las 4 capas de **Domain-Driven Design (DDD)**:
- **`src/Domain/`**:
  - **Bounded Context `Cliente`**: Raíz de agregado `Cliente`, Value Objects `DocumentoIdentidad` y `PerfilRiesgoCliente`.
  - **Bounded Context `Catalogo`**: Raíz de agregado `PlanSeguro`, Entidad hija `Cobertura` (con llave foránea `plan_id`), Value Object `TipoPlanVO`.
  - **Bounded Context `Poliza`**: Raíz de agregado `Poliza` (con métodos de dominio `descontarTechoAnualPoliza()`, `compensarCoberturaSaga()`, `restituirSaldoCobertura()`), Value Objects `BienAseguradoVehiculo`, `EstadoPolizaVO`, `PrimaMonetaria`, `VigenciaPoliza`, `UuidId`, y eventos `PolizaEmitidaEvent`, `CoberturaPolizaDescontadaEvent`, `CoberturaRestituidaEvent`.
  - **Bounded Context `Facturacion`**: Entidad `FacturaNotaVenta`, Value Object `NumeroComprobanteFiscal` y `FacturacionDomainService` (cálculo fiscal IVA 13% + IT 3%).
- **`src/Application/`**:
  - Servicios de Aplicación y Controladores ICONIX: `AuthOIDCController`, `ApolloFederationResolver`, `CatalogoPolizaApplicationService`, `EmisionPolizaGraphQLController`, `RecepcionPedidoService`, `FacturacionService`, `PolizaCoberturaService`.
- **`src/Infrastructure/`**:
  - Persistencia PDO PostgreSQL (`PdoPostgresConnection` conectado a Neon Serverless PostgreSQL con soporte de sincronización local), Repositorios DDD (`PostgresClienteRepository`, `PostgresPlanSeguroRepository`, `PostgresPolizaRepository`, `PostgresFacturaRepository`), `DynamoDbSessionCacheRepository`, `FacturaPdfGenerator` (generador nativo `%PDF-1.4` con hash `SHA-256`) y `SagaKafkaConsumer`.
- **`src/Presentation/GraphQL/`**:
  - `SupergraphGraphQLEngine` que sirve el contrato congelado `contracts/supergraph.graphql`.

---

## 2. Arquitectura de `frontend/mf2-clientes-react` (React 18+ PWA & Edge AI)
- **Sistema de Diseño**: Implementa la línea visual **"Executive Precision"** (`#005C55` Deep Emerald Teal, `#0F172A` Institutional Slate, `#4F46E5` AI Indigo, tipografías `Plus Jakarta Sans`, `Inter` y `JetBrains Mono`).
- **IA Local en Navegador (`ValidadorNitidezLocalWebControl.ts`)**:
  - Ejecuta convolución 2D con kernel Laplaciano $3 \times 3$ sobre el tensor RGBA en memoria del navegador antes de autorizar la mutación GraphQL `emitirPoliza`.
- **Soporte Offline-First PWA (`sw.js`, `manifest.json`, `ApolloFederationClient.ts`)**:
  - Permite encolar emisiones de pólizas cuando no hay conexión a internet asociando una llave `Idempotency-Key` (UUIDv4) y sincronizarlas automáticamente al recuperar señal.

---

## 3. Verificación y Pruebas Automatizadas
- **MS1 PHP 8.3 (`tests/run_tests.php`)**: `9 PASSED | 0 FAILED`.
- **MF2 React 18 PWA (`vitest run` & `vite build`)**: `4 PASSED | 0 FAILED` y compilación limpia en `dist/`.

