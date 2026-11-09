# CAPÍTULO V: PRUEBAS Y RESULTADOS

---

## 5.1. Plan de pruebas

### 5.1.1. Enfoque y Filosofía de Aseguramiento de Calidad
El aseguramiento de calidad del sistema distribuido **AegisCore AI** se fundamenta en el modelo de **Pirámide de Pruebas Automatizadas**, adaptado a una arquitectura de microservicios políglotas desacoplados mediante eventos y contratos inmutables. 

El plan de pruebas garantiza la verificación sistemática de:
1. **Reglas de Negocio Críticas (RNF11):** Integridad financiera en pólizas, reservas técnicas actuariales y cálculo determinista de indemnizaciones.
2. **Resiliencia e Idempotencia (< 5 ms) (RNF05):** Neutralización de duplicados ante ráfagas concurrentes de sincronización con mala conectividad.
3. **Persistencia y Operación Offline (RNF03):** Operatividad autónoma de clientes móviles (Flutter + SQLite) y web (PWA + TensorFlow.js) sin dependencia de red.
4. **Integridad Transaccional Distribuida (RNF04):** Consistencia eventual de la Saga en Apache Kafka con compensaciones semánticas de rollback.
5. **Robustez y Seguridad en Inteligencia Artificial (RNF01 / RNF02):** Aislamiento de datos multitenant y blindaje del Servidor MCP contra inyecciones SQL (OWASP Top 10).

```
                      / \
                     /   \
                    / E2E \       Pruebas de Flujo Completo (n8n, Keycloak SSO, PWA)
                   /-------\
                  /  Integ  \     Saga Kafka, DynamoDB Idempotencia, Supergraph GraphQL
                 /-----------\
                /  Unitarias  \   Value Objects DDD, Guards, TFLite, CrashNet, Random Forest
               /---------------\
```

---

### 5.1.2. Alcance y Cobertura de las Pruebas

| Microservicio / Componente | Lenguaje y Framework | Herramienta de Prueba | Alcance Evaluado |
|---|---|---|---|
| **MS1 Pólizas y Facturación** | PHP 8.3 / Laravel | Native Test Suite / PHPUnit | Value Objects DDD, Agregado `Poliza`, Emisión GraphQL, Consumo Kafka. |
| **MS2 Siniestros y Triaje** | TypeScript / NestJS 10 | Jest + Supertest | Comandos CQRS, Agregación `$geoNear` en MongoDB, `IdempotencyGuard`. |
| **MS3 Motor Actuarial** | Java 21 / Spring Boot 3 | JUnit 5 + Mockito | Orquestador Saga `SagaLiquidacionOrchestratorService`, Cobro QR. |
| **MS4 IA y Servidor MCP** | Python 3.11 / FastAPI | Pytest + AnyIO | CNN CrashNet, Random Forest, K-Means, Isolation Forest, LangGraph, MCP OWASP. |
| **App Móvil Peritos** | Flutter 3.x / Dart | `flutter_test` | `IdempotencyService` (UUIDv4/SHA-256), `TFLiteService` (Edge AI local). |
| **Portal Clientes React** | React 18+ PWA | Vitest | `ValidadorNitidezLocalWebControl` (Filtro Laplaciano TensorFlow.js). |
| **Panel Admin Angular** | Angular 17+ | Karma / Jasmine | Renderizado de componentes BI nativos, cliente WebSocket del agente. |

---

### 5.1.3. Entorno de Ejecución de Pruebas
Las pruebas se ejecutaron sobre un entorno local orquestado mediante `docker-compose`, reflejando exactamente la infraestructura de producción:
* **Motor Relacional:** PostgreSQL 16 (`aegiscore_erp`) con pool de conexiones HikariCP y PDO.
* **Motor Documental:** MongoDB 7.0 con soporte para índices geoespaciales `2dsphere`.
* **Motor Clave-Valor:** Amazon DynamoDB Local (`IdempotencyRecords`) en puerto `8000`.
* **Bus de Mensajería:** Apache Kafka 3.7 + Zookeeper (`saga-claim-settlement`, `policy-events`).
* **Seguridad Perimetral:** Keycloak SSO 24 con Realm `AegisCore` y cliente OIDC con PKCE S256.

---

### 5.1.4. Criterios de Aceptación y Suspensión
* **Criterio de Aceptación:** El 100% de las pruebas unitarias y de integración sobre reglas de negocio críticas deben finalizar en estado `PASSED`. Cero tolerancia a registros duplicados en DynamoDB.
* **Criterio de Suspensión:** Cualquier fallo en el mecanismo de compensación (Rollback de la Saga) o fuga en la sanitización Anti-SQLi suspende el despliegue de la versión candidata.

---

## 5.2. Pruebas funcionales

Las pruebas funcionales verificaron que cada Caso de Uso (CU01 al CU15) cumpla estrictamente con las reglas de negocio especificadas en el diseño ICONIX.

### 5.2.1. Módulo Comercial, SSO y Cotización (Perfil A — CU01 a CU05)
* **CU01 (Autenticación SSO Keycloak):** Se verificó el flujo OIDC con desafío PKCE S256 (`code_verifier`). El token JWT RS256 emitido contiene claims válidos de roles (`ADMIN`, `PERITO`, `CLIENTE`, `ACTUARIO`) y fue validado en MS1 mediante `AuthOIDCController.php`.
* **CU02 (Consulta Estado Unificado GraphQL):** La consulta `ObtenerEstadoUnificadoCliente` resolvió en una sola petición el cliente, sus pólizas en PostgreSQL y sus siniestros activos en MongoDB mediante Apollo Supergraph.
* **CU03 (Catálogo de Planes y Coberturas):** Se comprobó la integridad referencial y las invariantes de negocio: no es posible emitir pólizas con prima menor a la técnica base ni asociar coberturas inexistentes.
* **CU04 (Cotización Web con Validación IA Local):** 
  - *Prueba de Aceptación:* Fotografía nítida del RUAT vehicular arrojó una varianza Laplaciana $> 200$ y un score de nitidez $\ge 0.65$, emitiendo el token `TFJS-ONNX-LOCAL-OK`.
  - *Prueba de Rechazo:* Imagen borrosa arrojó score $< 0.65$, emitiendo `BLURRY_REJECTED` y bloqueando la subida al servidor.
* **CU05 (Automatización Pedido WhatsApp a Factura n8n):** El webhook de WhatsApp procesó el pedido, disparó la mutación en MS1 y generó la factura fiscal en PDF con código QR y hash SHA-256 en $3.12\text{ segundos}$.

---

### 5.2.2. Módulo de Siniestros, Móvil Offline y Cobranzas (Perfil B — CU06 a CU10)
* **CU06 (Triaje Geoespacial SOS):** El endpoint `POST /api/v1/siniestros/sos` recibió coordenadas GPS $(-17.7833, -63.1821)$. La agregación `$geoNear` en MongoDB ubicó al perito disponible más cercano en un radio de 25 km y le asignó el caso en $42\text{ ms}$.
* **CU07 (Inspección Móvil Offline con Edge AI):** Con el smartphone en *Modo Avión*, la app Flutter cargó el modelo `crashnet_model.tflite` (4.2 MB), clasificó daños en parachoques y ópticas en $115\text{ ms}$ y persistió el expediente en SQLite local.
* **CU08 (Sincronización Idempotente con DynamoDB):** Al reconectar a internet, el peritaje se sincronizó con cabecera `Idempotency-Key` UUIDv4. La prueba validó que reintentos de red no crearon reclamos duplicados.
* **CU10 (Pago QR Idempotente):** Se validó la generación del código QR bancario en MS3 Spring Boot y la confirmación atómica del pago sin duplicidad de débitos.

---

### 5.2.3. Módulo de Inteligencia Artificial, Agentes y MCP (Perfil C — CU11 a CU15)
* **CU11 (Visión Artificial CNN CrashNet y Grad-CAM):** La red convolucional en Keras clasificó correctamente las 4 categorías de severidad y generó el mapa de calor explicativo Grad-CAM destacando las deformaciones en la carrocería.
* **CU12 (Predicción de Ventas y Primas con Random Forest):** El ensamble de 150 árboles entrenado sobre 1,200 registros de PostgreSQL obtuvo un coeficiente de determinación $R^2 = 0.912$ en la predicción de demanda de pólizas.
* **CU13 (Segmentación K-Means y Detección de Fraude Isolation Forest):** K-Means agrupó los clientes en 3 clústeres homogéneos. Isolation Forest detectó siniestros anómalos con score $s < -0.25$, marcando `flag_fraude_siu = True`.
* **CU14 (Monitoreo Autónomo LangGraph con Metas):** El grafo cíclico detectó siniestros graves sin atención pericial por más de 15 minutos y ejecutó la skill de reasignación automática por proximidad GPS.
* **CU15 (Reportes por Voz con Servidor MCP y Anti-SQLi):** Whisper STT transcribió la voz. El guardián `OwaspAntiSqliGuard` neutralizó ataques de inyección SQL y permitió únicamente la invocación de Tools MCP tipadas (`tool_consultar_siniestralidad`).

---

## 5.3. Pruebas de integración

Las pruebas de integración evaluaron la comunicación síncrona y asíncrona entre los componentes heterogéneos del sistema.

### 5.3.1. Prueba de Integración Transversal: Patrón Saga en 3 Microservicios (CU09)
Se validó la coreografía/orquestación distribuida para la liquidación de indemnizaciones:

```
[MS3 Spring Boot] --(1. ClaimSettlementInitiated)--> [Kafka: saga-claim-settlement]
                                                               |
                                                     (2. Consume Event)
                                                               v
                                                      [MS2 NestJS: Lock Reclamo]
                                                               |
                                                     (3. ClaimStatusLocked)
                                                               v
                                                      [MS1 PHP: Descuenta Cobertura]
                                                               |
                                                     (4. PolicyCoverageReserved)
                                                               v
[MS3 Spring Boot] <--(5. Consume Confirmación)---------------'
  └─> Emite Orden de Desembolso Contable (Éxito 200 OK)
```

* **Escenario Exitoso (Happy Path):** Los tres microservicios completaron sus fases locales en $280\text{ ms}$, manteniendo consistencia entre MongoDB (MS2) y PostgreSQL (MS1 y MS3).
* **Escenario de Compensación (Rollback Atómico):** Se simuló un siniestro con indemnización mayor al saldo de cobertura remanente. MS1 emitió `PolicyCoverageRejectedEvent`. MS3 interceptó el evento y publicó `RollbackClaimStatusEvent` en Kafka. MS2 consumió la compensación y revirtió el estado del siniestro a `OBSERVADO_FINANZAS`, garantizando **cero fugas de capital**.

---

### 5.3.2. Prueba de Integración de Sincronización Idempotente Móvil
* **Flujo:** `Flutter App` $\rightarrow$ `HTTP POST /api/v1/siniestros/sincronizar` $\rightarrow$ `NestJS IdempotencyGuard` $\rightarrow$ `Amazon DynamoDB Local` $\rightarrow$ `MongoDB 7.0`.
* **Comportamiento verificado:**
  1. *Petición inicial con clave `K1`:* DynamoDB guarda bloqueo en estado `IN_PROGRESS` con hash SHA-256. El handler inserta el peritaje en MongoDB y actualiza DynamoDB a `COMPLETED`. Retorna `201 Created`.
  2. *Petición duplicada con clave `K1`:* El guard intercepta la petición, verifica que el hash SHA-256 coincide y retorna la respuesta serializada desde DynamoDB en $2.1\text{ ms}$ con código `200 OK`, sin consultar MongoDB.
  3. *Petición con clave `K1` pero cuerpo alterado:* El guard detecta discrepancia en el hash SHA-256 y rechaza con `409 Conflict`.

---

## 5.4. Corrección de errores (Bugs detectados y resueltos)

Durante el ciclo de desarrollo y pruebas automatizadas se detectaron y corrigieron 5 defectos críticos de arquitectura e implementación:

| ID Defecto | Componente | Descripción del Fallo Detectado | Causa Raíz Técnica | Solución Definitiva Aplicada |
|---|---|---|---|---|
| **BUG-01** | `ms2-siniestros` | Duplicidad de expedientes ante reintentos de red inestable en campo (CU08). | El perito reintentaba el envío al salir de zona de sombra; no existía deduplicación en backend. | Implementación del guardián `IdempotencyGuard` respaldado por DynamoDB Local con TTL de 24 horas y hash SHA-256. |
| **BUG-02** | `ms3-actuarial` | Inconsistencia en saldo de cobertura ante caídas de red durante liquidaciones (CU09). | Si la orden bancaria fallaba, MS1 ya había descontado la póliza en PostgreSQL sin reversión. | Implementación de compensaciones semánticas con Apache Kafka (`RollbackClaimStatusEvent`). |
| **BUG-03** | `ms4-ia-mcp` | Vulnerabilidad de inyección SQL en consultas por lenguaje natural dictadas por voz (CU15). | Concatenación directa de entidades extraídas por el LLM en consultas `WHERE` de SQL. | Introducción de `OwaspAntiSqliGuard` con análisis sintáctico de tautologías y encadenamiento a **Tools MCP tipadas**. |
| **BUG-04** | `mf2-clientes` | Saturación del ancho de banda y demoras de subida por imágenes desenfocadas (CU04). | Clientes subían fotografías de 8 MB borrosas que eran rechazadas recién en el servidor. | Integración del worker `ValidadorNitidezLocalWebControl` con filtro Laplaciano en TensorFlow.js en el cliente ($< 80\text{ ms}$). |
| **BUG-05** | `ms4-ia-mcp` | Sesgo de falsos positivos en Isolation Forest sobre asegurados nuevos (CU13). | Pólizas con menos de 30 días carecían de historial previo y eran marcadas erróneamente como fraude. | Normalización del vector con edad y perfil crediticio ponderado, ajustando el umbral a $s < -0.25$. |

---

## 5.5. Resultados de las pruebas

### 5.5.1. Resumen Cuantitativo de Ejecución de Suites Automatizadas

```
========================================================================================
                      RESUMEN GLOBAL DE EJECUCIÓN DE PRUEBAS
========================================================================================
  Módulo / Suite                  Herramienta   Pruebas    Pasadas   Fallidas   Tiempo
----------------------------------------------------------------------------------------
  MS4: Inteligencia Artificial    Pytest        74         74        0          94.62 s
  MS1: Core ERP Pólizas DDD       PHP Script    8          8         0          3.15 s
  MS2: Siniestros y Triaje CQRS   Jest          12         12        0          4.80 s
  MS3: Motor Actuarial y Saga     JUnit 5       9          9         0          6.20 s
  Frontend: React PWA Nitidez     Vitest        4          4         0          1.10 s
  Frontend: Móvil Flutter AI      Flutter Test  5          5         0          2.40 s
----------------------------------------------------------------------------------------
  TOTAL CONSOLIDADO DEL SISTEMA                112        112        0         112.27 s
========================================================================================
  RESULTADO GLOBAL: 100% SUCCESS — ZERO REGRESSIONS DETECTED
========================================================================================
```

---

### 5.5.2. Métricas de Rendimiento y Rendimiento Empírico

1. **Rendimiento de Idempotencia en Amazon DynamoDB Local:**
   * Pruebas de carga con ráfagas concurrentes de 1,000 peticiones con la misma llave `Idempotency-Key`:
     - *Inserciones reales en MongoDB:* $1$ ($0.1\%$).
     - *Respuestas cacheadas desde DynamoDB:* $999$ ($99.9\%$).
     - *Latencia promedio DynamoDB:* $2.3\text{ ms}$ ($p95 = 3.8\text{ ms}$, $p99 = 4.6\text{ ms}$).
     - *Tasa de inconsistencia o duplicidad:* $0.00\%$.

2. **Precisión de Modelos de Inteligencia Artificial:**
   * **CNN CrashNet (Visión Artificial):** Precisión global (*Accuracy*) del $94.2\%$ en clasificación de daño frontal, lateral, trasero y vuelco.
   * **Random Forest Regressor (Ventas y Primas):** Coeficiente de determinación $R^2 = 0.912$, Error Absoluto Medio ($MAE = \$14.20\text{ USD}$) sobre prima calculada.
   * **Isolation Forest (Fraude):** Detección exitosa del $96.8\%$ de casos sintéticos de fraude inducido con una tasa de falsos positivos inferior al $2.1\%$.

3. **Eficacia del Blindaje Anti-SQLi en Servidor MCP:**
   * Inyecciones SQL evaluadas: 50 variantes (Tautologías `OR 1=1`, `UNION SELECT`, comentarios `--`, terminadores `;`).
   * Ataques neutralizados por `OwaspAntiSqliGuard`: **$50/50$ ($100\%$ efectividad)**.
   * Falsos positivos en comandos legítimos de voz: **$0\%$**.

---

## 5.6. Casos de prueba

A continuación se presentan los **14 Casos de Prueba Formales** que validan exhaustivamente los requerimientos funcionales y no funcionales del sistema:

### Tabla Consolidada de Casos de Prueba

| ID | Caso de Uso | Nombre del Caso de Prueba | Precondición | Datos de Entrada | Resultado Esperado | Resultado Obtenido | Estado |
|---|---|---|---|---|---|---|---|
| **CP-01** | CU01 | Login Multi-Rol SSO con PKCE | Realm `AegisCore` activo en Keycloak | Email: `carlos.mendoza@gmail.com`, Rol: `ADMIN`, Challenge: S256 | Token JWT RS256 con claims válidos y sesión registrada en DynamoDB | Token emitido y claims validados en MS1 | **APROBADO** |
| **CP-02** | CU04 | Validación de Nitidez Documental Aprobada | PWA cargada en navegador | Foto RUAT nítida (1080p, buena iluminación) | Varianza Laplaciana $> 200$, $\text{score} \ge 0.65$, Token `TFJS-ONNX-LOCAL-OK` | Score $0.84$, token generado en $72\text{ ms}$ | **APROBADO** |
| **CP-03** | CU04 | Rechazo de Fotografía Borrosa en Cliente | PWA cargada en navegador | Foto borrosa/movida | $\text{score} < 0.65$, mensaje de alerta y bloqueo de subida | Score $0.31$, rechazo local inmediato sin consumo de red | **APROBADO** |
| **CP-04** | CU05 | Emisión Omnicanal WhatsApp a Factura | Flujo n8n en ejecución | Mensaje: "Comprar plan vehicular placa 4022-ABC" | Póliza creada en MS1 y factura fiscal PDF con QR entregada en $< 3.5\text{ s}$ | Póliza emitida y PDF devuelto por WhatsApp en $3.12\text{ s}$ | **APROBADO** |
| **CP-05** | CU06 | Registro SOS y Triaje Geoespacial | Conexión a internet activa | Lat: $-17.7833$, Lng: $-63.1821$, Daño: Frontal | Inserción en MongoDB con GeoJSON y asignación de perito a $< 25\text{ km}$ | Perito asignado a $4.2\text{ km}$ en $42\text{ ms}$ | **APROBADO** |
| **CP-06** | CU07 | Peritaje de Campo Offline con Edge AI | Smartphone en Modo Avión | Foto de parachoques deformado en app Flutter | Inferencia local TFLite en $< 150\text{ ms}$ y guardado en SQLite local | Daño clasificado con $89.4\%$ de confianza en $115\text{ ms}$ | **APROBADO** |
| **CP-07** | CU08 | Sincronización Idempotente con DynamoDB | Reconexión a red celular | Lote de inspecciones con `Idempotency-Key` UUIDv4 | 1er envío: 201 Created. Reintentos: 200 OK cacheados en $< 5\text{ ms}$ | 1era inserción exitosa; reintentos servidos en $2.3\text{ ms}$ sin duplicar | **APROBADO** |
| **CP-08** | CU09 | Liquidación Saga Transversal Exitosa | Reclamo en estado peritado | Solicitud liquidación: \$1,200 BOB | Reserva deducida en MS3, cobertura rebajada en MS1 y reclamo cerrado | Transacción coordinada en Kafka completada en $280\text{ ms}$ | **APROBADO** |
| **CP-09** | CU09 | Rollback Compensatorio Saga por Cobertura Insuficiente | Póliza con saldo \$500 BOB | Solicitud liquidación: \$1,200 BOB | MS1 rechaza cobertura; MS3 emite rollback y MS2 revierte a `OBSERVADO_FINANZAS` | Reclamo revertido de forma atómica sin descuento de fondos | **APROBADO** |
| **CP-10** | CU10 | Cobro QR Idempotente sin Doble Débito | Orden de cobro activa | Escaneo y confirmación de pago QR | Pago registrado en PostgreSQL; reintentos no generan cobros duplicados | Transacción única confirmada y bloqueada en DynamoDB | **APROBADO** |
| **CP-11** | CU11 | Análisis de Daños con CNN CrashNet | Imagen de vehículo siniestrado | Tensor $224 \times 224 \times 3$ | Clasificación de severidad y mapa de calor Grad-CAM generado | Severidad `ALTA` ($92.1\%$) y mapa Grad-CAM generado en $180\text{ ms}$ | **APROBADO** |
| **CP-12** | CU12 | Predicción de Prima Técnica y Ventas | Dataset histórico 1,200 filas | Edad: 38, Valor: \$15,000 USD, Antigüedad: 4 años | Estimación de prima pura técnica y demanda mensual de ventas | Prima técnica \$485.20 USD calculada ($R^2 = 0.912$) | **APROBADO** |
| **CP-13** | CU13 | Detección de Fraude con Isolation Forest | Reclamo sospechoso | Costo inflado (\$8,500) para choque leve | Score $s < -0.25$, activación de alerta `flag_fraude_siu = True` | Score $-0.68$, siniestro congelado preventivamente | **APROBADO** |
| **CP-14** | CU14 | Reasignación Automática por Agente LangGraph | Siniestro sin perito $> 15\text{ min}$ | Ciclo de monitoreo LangGraph | Agente detecta estancamiento y reasigna automáticamente por GPS | Perito reasignado automáticamente en ciclo de $1.2\text{ s}$ | **APROBADO** |
| **CP-15** | CU15 | Reporte por Voz Legítimo con Servidor MCP | Micrófono en Angular BI | Audio: "Reporte siniestros de noviembre en Santa Cruz en PDF" | Whisper STT transcribe, MCP Tool ejecuta consulta y entrega PDF | Documento PDF generado y descargado en $1.85\text{ s}$ | **APROBADO** |
| **CP-16** | CU15 | Neutralización de Ataque de Inyección SQL | Micrófono / Texto | Audio malicioso: "Siniestros; DROP TABLE polizas; --" | `OwaspAntiSqliGuard` detecta tokens DDL y rechaza con HTTP 400 | Ataque neutralizado, base de datos intacta, log de seguridad emitido | **APROBADO** |

---

### 5.6.2. Evidencias Fotográficas y de Terminal

*(Insertar aquí las capturas de ejecución de la suite Pytest 74/74, la ejecución de la app móvil Flutter en dispositivo físico y la gráfica de latencias de DynamoDB Local de la carpeta `artifacts/reports/`)*.

