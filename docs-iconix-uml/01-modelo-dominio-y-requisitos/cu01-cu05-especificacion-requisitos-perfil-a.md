# 📋 Especificación de Requisitos y Casos de Uso (CU01 al CU05) — Perfil A
## Metodología ICONIX & Estándar UML 2.5+ — AegisCore AI

---

### 🏛️ Identificación de la Célula de Trabajo
- **Célula:** Perfil A (Core Comercial, SSO Federado, Web React 18 PWA con IA Local en Navegador y Automatización n8n).
- **Materia:** Ingeniería de Software II (2do Parcial) — **Grupo:** #27.
- **Responsabilidad:** Microservicio 1 (`backend/ms1-polizas-php`), Micro-Frontend 2 (`frontend/mf2-clientes-react`), Contenedor Shell SSO (`frontend/sso-shell-container`), Keycloak SSO (`infra/keycloak-sso`) y Automatización n8n (`automation-n8n`).

---

## 📑 Índice de Casos de Uso del Perfil A
1. [CU01: Iniciar Sesión Único Multi-Aplicación (SSO) y Control de Roles](#-cu01-iniciar-sesión-único-multi-aplicación-sso-y-control-de-roles)
2. [CU02: Consultar Estado Unificado de Pólizas, Vehículos y Siniestros (Federación GraphQL)](#-cu02-consultar-estado-unificado-de-pólizas-vehículos-y-siniestros-federación-graphql)
3. [CU03: Gestionar Catálogo de Planes de Seguro, Coberturas (FK) y Clientes Asegurados](#-cu03-gestionar-catálogo-de-planes-de-seguro-coberturas-fk-y-clientes-asegurados)
4. [CU04: Cotizar y Emitir Póliza en Línea con Validación de Documentos por IA Local Web](#-cu04-cotizar-y-emitir-póliza-en-línea-con-validación-de-documentos-por-ia-local-web)
5. [CU05: Contratar o Renovar Póliza por WhatsApp y Emitir Factura / Nota de Venta PDF (n8n)](#-cu05-contratar-o-renovar-póliza-por-whatsapp-y-emitir-factura--nota-de-venta-pdf-n8n)
6. [Apoyo Transversal CU09 & CU10: Paso 2 Saga Cobertura en MS1 PHP y Cobro Prima QR Idempotente](#-apoyo-transversal-cu09--cu10-paso-2-saga-cobertura-en-ms1-php-y-cobro-prima-qr-idempotente)

---

## 🔐 CU01: Iniciar Sesión Único Multi-Aplicación (SSO) y Control de Roles

### 1. Ficha Técnica
| Atributo | Detalle |
|---|---|
| **Identificador** | `CU01` |
| **Nombre** | Iniciar sesión único (Single Sign-On) mediante OAuth 2.0 / OpenID Connect (PKCE S256) y control de roles RBAC entre Angular 17, React 18 PWA y Flutter. |
| **Actor Primario** | Asegurado (`CLIENTE`), Administrador (`ADMIN`), Actuario (`ACTUARIO`), Perito (`PERITO`). |
| **Disparador** | El usuario accede al Contenedor Shell SSO o a cualquiera de los Micro-Frontends sin sesión activa o solicita cambio de perfil. |
| **Precondiciones** | El Realm `aegiscore` se encuentra aprovisionado en Keycloak 24 (`infra/keycloak-sso/realm-aegiscore-export.json`) y la tabla `SesionesSSO` existe en Amazon DynamoDB. |
| **Postcondiciones** | Se emite un token JWT firmado con `RS256`, se registra la sesión unificada en DynamoDB (`SesionesSSO`) con TTL y se sincroniza el registro en PostgreSQL (`usuarios_roles`). |

### 2. Flujo Principal (Happy Path)
1. El usuario accede a la vista `LoginUnificadoSSOView` en el contenedor Shell SSO o en el Micro-Frontend React PWA.
2. El sistema genera criptográficamente el par PKCE (`code_verifier` y `code_challenge` con `SHA-256`).
3. La vista invoca el método `autenticarUsuarioOIDC()` del controlador `AuthOIDCController` (`POST /api/v1/auth/oidc-token`).
4. El controlador verifica las credenciales y el desafío PKCE contra la configuración del Realm `aegiscore` y firma el Access Token JWT con algoritmo `RS256`.
5. El controlador invoca `validarTokenJwtRS256()` para certificar la integridad de las claims (`sub`, `email`, `rol`, `cliente_id`, `realm_access.roles`).
6. El controlador ejecuta `registrarSesionUnificadaDynamoDB()` almacenando el documento `SesionUnificadaToken` en la tabla `SesionesSSO` de Amazon DynamoDB con latencia $< 5\text{ ms}$.
7. El controlador sincroniza los metadatos del usuario en la entidad relacional `UsuarioRol` de PostgreSQL (`usuarios_roles`).
8. La vista almacena el token JWT y habilita la navegación transversal entre el Dashboard Administrativo (`:4200`) y el Portal del Asegurado (`:3000`) sin exigir un segundo inicio de sesión.

### 3. Flujos Alternativos y Excepciones
- **FA-01.1 (Modo Offline PWA):** Si el servidor de identidad no responde por desconexión temporal, `AuthOIDCService` recupera la sesión validada en caché local y permite operar en modo lectura/encolado.
- **EX-01.1 (Token Expirado o Firma Inválida):** Si `validarTokenJwtRS256()` detecta expiración (`exp`) o alteración del payload, rechaza la petición con HTTP 401 (`Unauthorized`).

### 4. Trazabilidad ICONIX
- **Boundary:** `LoginUnificadoSSOView` (`frontend/sso-shell-container/src/index.html`, `frontend/mf2-clientes-react/src/App.tsx`).
- **Control:** `AuthOIDCController` (`backend/ms1-polizas-php/src/Application/Services/AuthOIDCController.php`, `frontend/sso-shell-container/src/AuthOIDCController.ts`) con métodos `autenticarUsuarioOIDC()`, `validarTokenJwtRS256()`, `registrarSesionUnificadaDynamoDB()`.
- **Entity:** `UsuarioRol` (PostgreSQL `usuarios_roles`), `SesionUnificadaToken` (Amazon DynamoDB `SesionesSSO`).

---

## 🌐 CU02: Consultar Estado Unificado de Pólizas, Vehículos y Siniestros (Federación GraphQL)

### 1. Ficha Técnica
| Atributo | Detalle |
|---|---|
| **Identificador** | `CU02` |
| **Nombre** | Consultar el estado unificado del asegurado en una sola petición GraphQL federando PostgreSQL, MongoDB y Amazon DynamoDB. |
| **Actor Primario** | Cliente Asegurado / Ejecutivo Comercial. |
| **Disparador** | El asegurado abre el panel principal `ResumenCoberturaClienteView` en el Micro-Frontend 2 (React 18 PWA). |
| **Precondiciones** | Sesión OIDC activa y contrato `contracts/supergraph.graphql` vigente. |
| **Postcondiciones** | Se presenta en una sola respuesta la ficha del cliente, pólizas activas, vehículos asegurados, saldo de cobertura restante, siniestros en curso y estado de caché DynamoDB. |

### 2. Flujo Principal (Happy Path)
1. La vista `ResumenCoberturaClienteView` envía una única operación `POST /graphql` con la query `ObtenerResumenUnificadoAsegurado($clienteId: ID!)`.
2. El motor `SupergraphGraphQLEngine` delega la ejecución al objeto de control `ApolloFederationResolver` mediante el método `resolverResumenUnificadoAsegurado()`.
3. El resolver consulta en Neon PostgreSQL (`aegiscore_erp`) la entidad `Cliente`, sus `Poliza` activas, el `PlanSeguro` asociado, las `Cobertura` (FK) y las `FacturaNotaVenta` pendientes.
4. El resolver invoca `consultarOActualizarCacheCoberturaActiva()` contra la tabla `CacheCoberturaActiva` en Amazon DynamoDB para recuperar o refrescar el saldo disponible en $< 5\text{ ms}$.
5. El resolver invoca `federarExpedientesSiniestrosMongoDB()` para cruzar por `numeroPoliza` / `polizaId` los expedientes de siniestros alojados en MongoDB Atlas (`aegiscore_siniestros`), incluyendo triaje IA y peritaje móvil.
6. El resolver ensambla el objeto `ResumenUnificadoPayload` respetando estrictamente `contracts/supergraph.graphql`.
7. La vista React renderiza los indicadores KPI, barras de progreso de cobertura anual, inspector de query GraphQL y estado de los 3 motores de base de datos.

### 3. Flujos Alternativos y Excepciones
- **FA-02.1 (Cache Hit DynamoDB):** Si el saldo de cobertura no ha sufrido mutaciones por Saga, se sirve directamente desde `CacheCoberturaActiva`.
- **EX-02.1 (Cliente Inexistente):** Si el `clienteId` no existe en PostgreSQL, el resolver utiliza el asegurado titular demostrable o retorna error tipado en el arreglo `errors` de GraphQL.

### 4. Trazabilidad ICONIX
- **Boundary:** `ResumenCoberturaClienteView` (`frontend/mf2-clientes-react/src/App.tsx`), Endpoint `POST /graphql`.
- **Control:** `ApolloFederationResolver` (`backend/ms1-polizas-php/src/Application/Services/ApolloFederationResolver.php`) con métodos `resolverResumenUnificadoAsegurado()`, `consultarOActualizarCacheCoberturaActiva()`, `federarExpedientesSiniestrosMongoDB()`.
- **Entity:** `Poliza` y `Cliente` (PostgreSQL), `ExpedienteSiniestro` (MongoDB), `CacheCoberturaActiva` (Amazon DynamoDB).

---

## 🗂️ CU03: Gestionar Catálogo de Planes de Seguro, Coberturas (FK) y Clientes Asegurados

### 1. Ficha Técnica
| Atributo | Detalle |
|---|---|
| **Identificador** | `CU03` |
| **Nombre** | Administrar el catálogo comercial de Planes de Seguro, Coberturas relacionales con llave foránea (`plan_id`) y Clientes bajo arquitectura DDD en PHP 8.3. |
| **Actor Primario** | Administrador Comercial / Suscriptor de Seguros. |
| **Disparador** | El usuario accede a la pestaña `GestionCatalogoSegurosView` y registra un nuevo Plan, Cobertura o Cliente. |
| **Precondiciones** | Conexión activa con PostgreSQL (`planes_seguro`, `coberturas_plan`, `clientes`). |
| **Postcondiciones** | Los agregados DDD son validados por sus Value Objects e insertados transaccionalmente en PostgreSQL. |

### 2. Flujo Principal (Happy Path)
1. El administrador ingresa a `GestionCatalogoSegurosView` y consulta el catálogo actual invocando `listarPlanesSeguro()`.
2. Para crear un nuevo plan, completa el código único, nombre comercial, tipo de plan (`TipoPlanVO`), prima base anual (`PrimaMonetaria`) y porcentaje de deducible.
3. La vista invoca la mutación GraphQL `registrarPlanSeguro` que delega en `CatalogoPolizaApplicationService::registrarPlanSeguroDDD()`.
4. El servicio de aplicación instancia la raíz de agregado `PlanSeguro` (`Domain/Catalogo/Entities/PlanSeguro.php`) y sus entidades hijas `Cobertura` (`Domain/Catalogo/Entities/Cobertura.php`), verificando invariantes de dominio (suma asegurada $> 0$, código en mayúsculas).
5. El repositorio `PostgresPlanSeguroRepository` persiste el plan en `planes_seguro` y sus coberturas vinculadas mediante llave foránea `plan_id` en `coberturas_plan`.
6. Para dar de alta un nuevo cliente asegurado, la vista invoca `registrarClienteDDD()`, el cual valida `DocumentoIdentidad` y `PerfilRiesgoCliente` e inserta el registro en la tabla `clientes`.

### 3. Flujos Alternativos y Excepciones
- **FA-03.1 (Adición de Cobertura a Plan Existente):** Mediante `agregarCoberturaAPlan()`, el administrador vincula una nueva entidad `Cobertura` a un `PlanSeguro` existente respetando la integridad referencial (`FK plan_id`).
- **EX-03.1 (Violación de Invariante DDD):** Si la prima base es $\le 0$ o el documento de identidad es inválido, `DomainException` aborta la transacción antes de tocar la base de datos.

### 4. Trazabilidad ICONIX
- **Boundary:** `GestionCatalogoSegurosView` (`frontend/mf2-clientes-react/src/App.tsx`).
- **Control:** `CatalogoPolizaApplicationService` (`backend/ms1-polizas-php/src/Application/Services/CatalogoPolizaApplicationService.php`) con métodos `listarPlanesSeguro()`, `registrarPlanSeguroDDD()`, `agregarCoberturaAPlan()`, `registrarClienteDDD()`.
- **Entity:** Raíz de Agregado `PlanSeguro`, Entidad Hija `Cobertura` (FK `plan_id`), Raíz de Agregado `Cliente` (PostgreSQL).

---

## 🧠 CU04: Cotizar y Emitir Póliza en Línea con Validación de Documentos por IA Local Web

### 1. Ficha Técnica
| Atributo | Detalle |
|---|---|
| **Identificador** | `CU04` |
| **Nombre** | Cotizar prima anual/mensual y emitir póliza en línea exigiendo validación previa de nitidez documental en el navegador con IA Local Web (ONNX / TensorFlow.js) y soporte Offline PWA. |
| **Actor Primario** | Cliente Asegurado. |
| **Disparador** | El asegurado solicita cotización vehicular y adjunta fotografía del RUAT / Cédula / Vehículo para emitir su póliza. |
| **Precondiciones** | Plan de seguro seleccionado y navegador web con soporte HTML5 Canvas / WebAssembly. |
| **Postcondiciones** | Si el score de nitidez local es $\ge 0.65$, se emite la póliza en PostgreSQL (o se encola con `Idempotency-Key` si está offline) y se publica el evento `PolizaEmitidaEvent`. |

### 2. Flujo Principal (Happy Path)
1. El asegurado ingresa a `CotizadorInscripcionWebView`, selecciona un plan y completa los datos del vehículo (`placa`, `vin`, `marca`, `modelo`, `anio`, `valorComercial`).
2. Presiona **"Cotizar Póliza"**, invocando la mutación `cotizarPolizaEnLinea` atendida por `EmisionPolizaGraphQLController::cotizarPolizaEnLinea()` y `CotizacionPolizaDomainService`.
3. Antes de permitir la emisión, el asegurado carga o simula la fotografía del documento en el escáner local del navegador.
4. El objeto de control `ValidadorNitidezLocalWebControl` ejecuta `validarNitidez()` **100% en el navegador del cliente**:
   - Convierte el tensor RGBA a luminancia ITU-R BT.601:
     $$Y = 0.299 R + 0.587 G + 0.114 B$$
   - Aplica convolución 2D con el kernel Laplaciano $3 \times 3$:
     $$L = \begin{bmatrix} 0 & 1 & 0 \\ 1 & -4 & 1 \\ 0 & 1 & 0 \end{bmatrix}$$
   - Calcula la varianza Laplaciana $\sigma^2_L$ y la normaliza al rango $[0, 1]$.
5. Si `nitidezScore >= 0.65`, `ValidadorNitidezLocalWebControl` firma el token local `TFJS-ONNX-LOCAL-OK-...` y desbloquea el botón de emisión.
6. La vista envía la mutación GraphQL `emitirPoliza` junto con la cabecera `Idempotency-Key` (UUIDv4) y el `tokenValidacionNitidezLocal`.
7. `EmisionPolizaGraphQLController::insertarPoliza()` verifica el token de nitidez, construye el agregado `Poliza`, persiste el contrato en PostgreSQL, genera la primera factura y actualiza el caché en DynamoDB.

### 3. Flujos Alternativos y Excepciones
- **FA-04.1 (Emisión Offline PWA):** Si el navegador se encuentra sin conexión (`isOffline = true`), `ApolloFederationClient` almacena la operación en la cola local con su `Idempotency-Key` y la sincroniza automáticamente al recuperar red.
- **EX-04.1 (Documento Borroso / Motion Blur):** Si `nitidezScore < 0.65`, el control bloquea la emisión en el cliente sin consumir ancho de banda ni GPU del servidor, mostrando alerta diagnóstica.

### 4. Trazabilidad ICONIX
- **Boundary:** `CotizadorInscripcionWebView` (`frontend/mf2-clientes-react/src/App.tsx`).
- **Control:** `ValidadorNitidezLocalWebControl` (`validarNitidez()`) en el cliente web + `EmisionPolizaGraphQLController` (`cotizarPolizaEnLinea()`, `validarNitidez()`, `insertarPoliza()`) en MS1 PHP.
- **Entity:** Raíz de Agregado `Poliza`, Value Object `BienAseguradoVehiculo` (PostgreSQL `polizas`).

---

## 💬 CU05: Contratar o Renovar Póliza por WhatsApp y Emitir Factura / Nota de Venta PDF (n8n)

### 1. Ficha Técnica
| Atributo | Detalle |
|---|---|
| **Identificador** | `CU05` |
| **Nombre** | Automatizar la contratación o renovación de póliza desde WhatsApp mediante flujo n8n y emitir Factura Fiscal / Nota de Venta en formato PDF con sello SHA-256. |
| **Actor Primario** | Cliente Asegurado vía WhatsApp / Orquestador Automatizado n8n. |
| **Disparador** | El cliente envía los datos de su vehículo por WhatsApp o se dispara el webhook de contratación hacia n8n. |
| **Precondiciones** | Flujo `automation-n8n/workflow-pedido-poliza-whatsapp-factura.json` configurado y servicio `FacturacionService` activo en MS1 PHP. |
| **Postcondiciones** | Se crea la `Poliza` con canal `WHATSAPP_N8N`, se persiste la `FacturaNotaVenta` con desglose de impuestos (IVA 13% + IT 3%), se genera el binario PDF (`%PDF-1.4`) con hash `SHA-256` y se responde al cliente con el enlace de descarga. |

### 2. Flujo Principal (Happy Path)
1. El cliente envía su solicitud de póliza al `BotConversacionalWhatsAppPoliza` indicando documento de identidad, placa, marca, modelo, año y valor comercial.
2. El nodo `WebhookTriggerN8N` del flujo n8n recibe el mensaje JSON, normaliza los campos y realiza la petición HTTP `POST /api/v1/whatsapp/pedido-poliza` hacia MS1 PHP.
3. El controlador `RecepcionPedidoService` ejecuta `procesarPedidoPolizaWhatsApp()`: localiza o crea al asegurado en PostgreSQL, calcula la prima anual con base en el plan seleccionado e inserta la nueva `Poliza` activa.
4. A continuación, `RecepcionPedidoService` delega al control `FacturacionService` mediante el método `generarFacturaNotaVentaPDF()`.
5. `FacturacionDomainService` calcula el subtotal neto, los impuestos de ley y el total facturado, instanciando la entidad `FacturaNotaVenta` con su `NumeroComprobanteFiscal` (`FAC-2026-...`).
6. El generador de infraestructura `FacturaPdfGenerator` construye en memoria el documento binario estándar `%PDF-1.4` con los datos fiscales del asegurado, número de póliza y vehículo, calculando su huella criptográfica `hash_digital_sha256`.
7. El repositorio `PostgresFacturaRepository` guarda la factura en la tabla `facturas_notas_venta` de PostgreSQL.
8. El flujo n8n recibe la respuesta JSON con `url_pdf` y `hash_digital_sha256` y despacha el comprobante PDF directamente al WhatsApp y correo electrónico del asegurado.

### 3. Flujos Alternativos y Excepciones
- **FA-05.1 (Descarga Directa del Binario PDF):** Al invocar `GET /api/v1/facturas/{id}/pdf`, `FacturacionService::obtenerBinarioPdfFactura()` entrega el flujo `application/pdf` listo para impresión o archivo contable.

### 4. Trazabilidad ICONIX
- **Boundary:** `BotConversacionalWhatsAppPoliza` (Webhook WhatsApp / Simulador en React PWA).
- **Control:** `WebhookTriggerN8N` (`automation-n8n/workflow-pedido-poliza-whatsapp-factura.json`), `RecepcionPedidoService` (`procesarPedidoPolizaWhatsApp()`) y `FacturacionService` (`generarFacturaNotaVentaPDF()`).
- **Entity:** `Poliza` (PostgreSQL `polizas`) y `FacturaNotaVenta` (PostgreSQL `facturas_notas_venta`).

---

## 🔄 Apoyo Transversal CU09 & CU10: Paso 2 Saga Cobertura en MS1 PHP y Cobro Prima QR Idempotente

### 1. Participación del Perfil A en CU09 (Saga de Liquidación en MS1 PHP)
- **Control:** `PolizaCoberturaService` (`backend/ms1-polizas-php/src/Application/Services/PolizaCoberturaService.php`) y `SagaKafkaConsumer`.
- **Métodos Operacionales UML 2.5+:**
  - `descontarTechoAnualPoliza()`: Ejecuta el **Paso 2 de la Saga** descontando el monto de indemnización del `saldo_cobertura_restante` de la póliza en PostgreSQL y emitiendo el evento `CoberturaPolizaDescontadaEvent`.
  - `compensarCoberturaSaga()` / `restituirSaldoCobertura()`: Ejecuta la **transacción compensatoria (Rollback)** cuando MS3 Actuarial reporta fallo en la reserva técnica, restituyendo íntegramente el saldo de cobertura a la póliza y actualizando DynamoDB.

### 2. Participación del Perfil A en CU10 (Pasarela de Pago Prima QR en React PWA y MS1 PHP)
- **Boundary:** `PasarelaPagoPrimaQRView` en React 18 PWA (`frontend/mf2-clientes-react/src/App.tsx`).
- **Control:** Endpoint `POST /api/v1/pagos-qr` con verificación de cabecera obligatoria `Idempotency-Key` (UUIDv4) en Amazon DynamoDB (`IdempotencyRecords`) y persistencia ACID en PostgreSQL (`pagos_prima_qr`), garantizando **cero doble cobro** ante reintentos por microcortes de señal.

