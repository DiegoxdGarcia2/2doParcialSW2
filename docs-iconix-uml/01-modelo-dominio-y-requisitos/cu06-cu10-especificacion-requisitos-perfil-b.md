# 📋 Especificación de Requisitos y Casos de Uso (CU06 al CU10) — Perfil B
## Metodología ICONIX & Estándar UML 2.5+ — AegisCore AI

---

### 🏛️ Identificación de la Célula de Trabajo
- **Célula:** Perfil B (Siniestros, Movilidad en Campo 100% Offline, Idempotencia Distribuida y Transacción Saga en 3 Microservicios).
- **Materia:** Ingeniería de Software II (2do Parcial) — **Grupo:** #27.
- **Responsabilidad:** Microservicio 2 (`backend/ms2-siniestros-nestjs`), Microservicio 3 (`backend/ms3-actuarial-springboot`) y App Móvil Flutter (`frontend/app-peritos-flutter`).

---

## 📑 Índice de Casos de Uso del Perfil B
1. [CU06: Reportar Siniestro Vial de Emergencia Directo desde App Móvil con Triaje IA](#-cu06-reportar-siniestro-vial-de-emergencia-directo-desde-app-móvil-con-triaje-ia)
2. [CU07: Inspeccionar Daños Offline en Terreno con Agente de IA Local (TFLite & SQLite)](#-cu07-inspeccionar-daños-offline-en-terreno-con-agente-de-ia-local-tflite--sqlite)
3. [CU08: Sincronizar Expediente de Siniestro con Control de Idempotencia en DynamoDB](#-cu08-sincronizar-expediente-de-siniestro-con-control-de-idempotencia-en-dynamodb)
4. [CU09: Liquidar y Pagar Indemnización de Siniestro (Patrón Saga en 3 Microservicios con Rollback Kafka)](#-cu09-liquidar-y-pagar-indemnización-de-siniestro-patrón-saga-en-3-microservicios-con-rollback-kafka)
5. [CU10: Procesar Cobro Recurrente de Primas y Pago QR Idempotente](#-cu10-procesar-cobro-recurrente-de-primas-y-pago-qr-idempotente)

---

## 🚨 CU06: Reportar Siniestro Vial de Emergencia Directo desde App Móvil con Triaje IA

### 1. Ficha Técnica
| Atributo | Detalle |
|---|---|
| **Identificador** | `CU06` |
| **Nombre** | Reportar siniestro vial de emergencia (Botón SOS) con captura de telemetría GPS, fotos de colisión y triaje automático de severidad. |
| **Actor Primario** | Asegurado accidentado / Perito de guardia. |
| **Disparador** | El asegurado pulsa el botón SOS de emergencia ante una colisión o avería vial. |
| **Precondiciones** | El asegurado cuenta con la app instalada y una póliza de automotor activa. El dispositivo móvil dispone de sensor GPS habilitado. |
| **Postcondiciones** | Se crea el documento del siniestro en MongoDB con índice geoespacial `2dsphere`, se clasifica la severidad preliminar (`LEVE`, `MODERADO`, `GRAVE`) y se despacha la alerta de auxilio al perito más cercano. |

### 2. Flujo Principal (Happy Path)
1. El asegurado abre la app móvil y pulsa el botón destacado **"CU06: Reporte SOS de Emergencia"**.
2. La vista captura automáticamente las coordenadas de geolocalización satelital (latitud y longitud precisas).
3. El asegurado indica el número de heridos, si el vehículo quedó inmovilizado y si se desplegaron los airbags, agregando una descripción y fotografías del choque.
4. Presiona **"EMITIR ALERTA SOS INMEDIATA"**.
5. La app genera un `Idempotency-Key` (UUIDv4) y emite un `POST /api/v1/siniestros/sos` hacia el microservicio MS2 (NestJS).
6. El `IdempotencyGuard` valida el encabezado y adquiere el bloqueo transaccional en Amazon DynamoDB Local.
7. El caso de uso `RegistrarSiniestroHandler` (CQRS Command) instancia el Aggregate Root `ReclamoSiniestro` en el dominio puro.
8. La clase de dominio `SeveridadVO.calcularTriaje()` evalúa la severidad en función de los heridos y deformaciones estructurales.
9. El repositorio `MongoReclamoRepository` persiste el expediente en la colección `expedientes_siniestros` de MongoDB con tipo `Point` GeoJSON.
10. El adaptador `FcmNotificationAdapter` despacha una notificación push a los peritos en guardia dentro del radio geográfico de cobertura.
11. DynamoDB actualiza el registro a estado `COMPLETED` y MS2 retorna `HTTP 201 Created` con el identificador de reclamo generado (`REC-2026-XXXXX`).
12. La app móvil muestra en pantalla la confirmación de asistencia en camino y el tiempo estimado de arribo.

### 3. Flujos Alternativos y Excepciones
- **FA-06.1 (Reintento de red por intermitencia 3G/4G):** Si el asegurado reenvía la solicitud tras un corte de señal, el `IdempotencyGuard` detecta la clave en DynamoDB y responde en $<5$ ms con `X-Cache-Lookup: HIT_IDEMPOTENCY_DYNAMODB`, evitando duplicar el expediente del siniestro.
- **EX-06.1 (Falta de coordenadas GPS):** Si el usuario desactivó el GPS de su móvil, el sistema solicita ingresar una referencia textual de dirección física antes de despachar la solicitud.
- **EX-06.2 (Póliza Inexistente o Vencida):** Si el número de póliza no es válido, el sistema asigna el siniestro a estado `OBSERVADO_COBERTURA` para auditoría previa al envío de perito.

### 4. Trazabilidad ICONIX
- **Boundary:** `SosEmergencyScreen` (Flutter), `PushNotificationFCMBoundary`, `POST /api/v1/siniestros/sos`.
- **Control:** `RegistrarSiniestroHandler` (MS2 NestJS CQRS), `IdempotencyGuard`, `SeveridadVO.calcularTriaje()`.
- **Entity:** `ReclamoSiniestro` (Dominio NestJS), `expedientes_siniestros` (MongoDB 2dsphere), `IdempotencyRecords` (DynamoDB).

---

## 📱 CU07: Inspeccionar Daños Offline en Terreno con Agente de IA Local (TFLite & SQLite)

### 1. Ficha Técnica
| Atributo | Detalle |
|---|---|
| **Identificador** | `CU07` |
| **Nombre** | Ejecutar inspección técnica pericial sin internet, con inferencia local Edge AI (TensorFlow Lite) y persistencia en base de datos local SQLite. |
| **Actor Primario** | Perito de campo en terreno. |
| **Disparador** | El perito llega al lugar del accidente (carretera o sótano sin cobertura celular) y procede a evaluar los daños materiales. |
| **Precondiciones** | La aplicación móvil tiene precargado el modelo de clasificación cuantizado `damage_classifier.tflite` y sus etiquetas. |
| **Postcondiciones** | El informe de peritaje queda registrado en la base de datos SQLite local del teléfono con hash de integridad SHA-256 y estado `PENDIENTE_SYNC`. |

### 2. Flujo Principal (Happy Path)
1. El perito accede a **"CU07: Peritaje Offline + Edge AI"** en su teléfono móvil.
2. Ingresa o escanea el ID de siniestro (`REC-2026-00050`) y sus credenciales de perito inspector.
3. Apunta la cámara del smartphone hacia la zona del vehículo dañada (parachoques, capó, faroles o puertas) y pulsa **"EVALUAR PIEZA CON EDGE AI (TFLITE)"**.
4. El servicio `TFLiteService` ejecuta la inferencia on-device directamente sobre la CPU/NPU del dispositivo móvil con el modelo cuantizado `damage_classifier.tflite`.
5. El modelo clasifica el componente vehicular y calcula el grado de severidad y certeza probabilística (ej. *Parachoques*, severidad *Moderada*, confianza: *88%*).
6. La app muestra la tarjeta de diagnóstico con costo sugerido en moneda nacional (BOB). El perito valida o ajusta la cotización de repuestos y mano de obra.
7. El perito agrega la pieza evaluada al inventario del peritaje y documenta sus notas técnicas.
8. Pulsa **"GUARDAR PERITAJE EN SQLITE LOCAL (OFFLINE)"**.
9. La clase `IdempotencyService` genera un `Idempotency-Key` (UUIDv4) y calcula el hash SHA-256 del contenido pericial.
10. La clase `DatabaseHelper` inserta la inspección en la tabla local `inspecciones_locales` y los ítems en `partes_danadas_locales` de SQLite.
11. La app notifica con un badge verde de seguridad: *"Peritaje Guardado Localmente en SQLite (100% Offline)"*.

### 3. Flujos Alternativos y Excepciones
- **FA-07.1 (Evaluación Multi-Pieza):** El perito puede evaluar secuencialmente parachoques, capó y ópticas; la interfaz acumula el presupuesto total antes del guardado atómico en SQLite.
- **EX-07.1 (Falla de inicialización de tensores):** Si el dispositivo móvil carece de soporte para aceleración de tensores, el `TFLiteService` recurre al clasificador heurístico local determinista con matriz de fallas.

### 4. Trazabilidad ICONIX
- **Boundary:** `PeritajeCaptureScreen` (Flutter Camera & UI), Sensor GPS local.
- **Control:** `TFLiteService` (Inferencia on-device), `DatabaseHelper` (Gestor de transacciones SQLite), `IdempotencyService`.
- **Entity:** `aegiscore_offline_peritajes.db` (SQLite en disco del celular: tablas `inspecciones_locales` y `partes_danadas_locales`).

---

## 🔄 CU08: Sincronizar Expediente de Siniestro con Control de Idempotencia en DynamoDB

### 1. Ficha Técnica
| Atributo | Detalle |
|---|---|
| **Identificador** | `CU08` |
| **Nombre** | Sincronizar expedientes levantados offline hacia el backend MS2 mediante el protocolo estricto `Idempotency-Key` (UUIDv4 + Hash SHA-256) validado en DynamoDB Local. |
| **Actor Primario** | Perito ajustador / Background Sync Worker de la app móvil. |
| **Disparador** | El perito recupera la conexión a internet o pulsa el botón de sincronización de cola. |
| **Precondiciones** | Existen inspecciones en estado `PENDIENTE_SYNC` en la base de datos local SQLite del teléfono móvil. |
| **Postcondiciones** | Los peritajes se consolidan en MongoDB Atlas con estado `PERITAJE_COMPLETADO`, la tabla SQLite local se marca como `SINCRONIZADO EN NUBE`, y la clave queda sellada en DynamoDB evitando cualquier duplicado. |

### 2. Flujo Principal (Happy Path)
1. El perito ingresa a la pantalla **"CU08: Sincronización Idempotente (DynamoDB)"**.
2. La vista lista los peritajes pendientes almacenados en SQLite en la pestaña **"En Cola SQLite (N)"**.
3. El perito presiona el botón **"SINCRONIZAR COLA CON MS2 Y DYNAMODB"**.
4. La app extrae el registro de SQLite junto con su `Idempotency-Key` UUIDv4 y su hash SHA-256 previamente calculados.
5. El cliente `ApiClient` construye los encabezados HTTP según el contrato congelado `contracts/idempotency-header.spec.json`:
   ```http
   Idempotency-Key: fe1b51e8-e627-4b87-abbe-99e6ae190854
   X-Client-Id: FLUTTER_MOBILE
   Content-Type: application/json
   ```
6. El backend MS2 recibe la petición en `POST /api/v1/siniestros/peritaje/sync`.
7. El `IdempotencyGuard` intercepta la solicitud y consulta la tabla `AegisCore_IdempotencyRecords` en DynamoDB Local por Partition Key.
8. Al no existir registro previo, DynamoDB crea un ítem con estado `PROCESSING` para adquirir el bloqueo exclusivo.
9. El caso de uso `SincronizarPeritajeHandler` valida la estructura, recupera o asocia el siniestro en MongoDB y actualiza el expediente con las piezas, fotos y costos estimados.
10. El estado del expediente en MongoDB transiciona formalmente a `PERITAJE_COMPLETADO`.
11. DynamoDB actualiza el registro con estado `COMPLETED`, código `200` y el JSON de respuesta.
12. La app móvil recibe `HTTP 200 OK`, actualiza la fila en SQLite con `estado_sync = 'SINCRONIZADO'`, y mueve la tarjeta a la pestaña **"Sincronizados (1)"**.

### 3. Flujos Alternativos y Excepciones
- **FA-08.1 (Reintento de red con misma clave y mismo hash - Cache Hit):** Si la red se corta antes de que el móvil reciba la respuesta y el perito reintenta la sincronización, DynamoDB detecta el estado `COMPLETED` y devuelve la respuesta en caché en $< 5$ ms con el encabezado:
  ```http
  X-Cache-Lookup: HIT_IDEMPOTENCY_DYNAMODB
  ```
  La app móvil procesa la confirmación sin que MS2 haya ejecutado escrituras duplicadas en MongoDB.
- **EX-08.1 (Petición concurrente en curso):** Si dos hilos envían la misma clave simultáneamente, el guard detecta `status = PROCESSING` y retorna `HTTP 409 Conflict` (`CONCURRENT_REQUEST_IN_PROGRESS`).
- **EX-08.2 (Payload alterado con misma clave):** Si el hash SHA-256 no coincide con el guardado en DynamoDB, el sistema devuelve `HTTP 422 Unprocessable Entity` por violación de integridad criptográfica.

### 4. Trazabilidad ICONIX
- **Boundary:** `SyncQueueScreen` (Flutter), `POST /api/v1/siniestros/peritaje/sync`.
- **Control:** `IdempotencyGuard` (NestJS Interceptor), `SincronizarPeritajeHandler` (CQRS Command), `DynamoIdempotencyRepository`.
- **Entity:** `AegisCore_IdempotencyRecords` (DynamoDB Local), `expedientes_siniestros` (MongoDB 7), `inspecciones_locales` (SQLite).

---

## ⚖️ CU09: Liquidar y Pagar Indemnización de Siniestro (Patrón Saga en 3 Microservicios con Rollback Kafka)

### 1. Ficha Técnica
| Atributo | Detalle |
|---|---|
| **Identificador** | `CU09` |
| **Nombre** | Orquestar la transacción distribuida transversal de liquidación de indemnización a través de 3 microservicios políglotas (MS2 NestJS, MS1 PHP y MS3 Spring Boot) con compensación semántica (Rollback en Kafka). |
| **Actor Primario** | Ajustador de siniestros / Gerente de Finanzas / Orquestador Saga. |
| **Disparador** | El ajustador autoriza la liquidación económica del expediente peritado desde el panel administrativo o móvil. |
| **Precondiciones** | El siniestro está en estado `PERITAJE_COMPLETADO` con monto aprobado. Apache Kafka se encuentra operativo con los tópicos `aegiscore.saga.*`. |
| **Postcondiciones** | Se bloquea el siniestro en MS2, se debita la cobertura en la póliza en MS1, se autoriza el desembolso en MS3, y se notifica al asegurado. Ante cualquier fallo en el paso final, se ejecutan transacciones compensatorias en orden inverso. |

### 2. Flujo Principal (Happy Path)
1. El ajustador solicita la liquidación invocando `POST /api/v1/liquidaciones/iniciar` en el microservicio MS3 (Spring Boot Hexagonal).
2. El puerto de entrada `LiquidarSiniestroSagaUseCasePort` recibe la orden y el servicio `SagaLiquidacionOrchestratorService` crea una instancia de Saga con estado `INICIADA` en PostgreSQL.
3. **Paso 1 (Bloqueo de Siniestro en MS2):**
   - MS3 emite el comando `MarcarReclamoEnLiquidacionCommand` al tópico Kafka `aegiscore.saga.commands`.
   - El servicio `KafkaSagaConsumerService` de MS2 consume el mensaje y ejecuta `MarcarEnLiquidacionHandler`.
   - MS2 actualiza el expediente a `EN_PROCESO_LIQUIDACION` en MongoDB y publica `ReclamoMarcadoEnLiquidacionEvent` en `aegiscore.saga.events`.
4. **Paso 2 (Descuento de Cobertura en MS1 PHP):**
   - MS3 consume el evento de MS2 y emite `DescontarCoberturaPolizaCommand` a Kafka.
   - MS1 (PHP DDD) verifica la vigencia de la póliza en PostgreSQL, descuenta el saldo de cobertura y publica `CoberturaPolizaDescontadaEvent`.
5. **Paso 3 (Aprobación Actuarial y Desembolso en MS3):**
   - MS3 consume el evento de MS1 y el servicio de dominio `CalculoActuarialService` valida la disponibilidad en el fondo de reservas técnicas.
   - Al haber solvencia técnica suficiente, MS3 asienta la orden de liquidación en la tabla PostgreSQL `orden_liquidacion_saga` con estado `APROBADA`.
   - MS3 emite el evento final `SagaLiquidacionCompletadaEvent` en Kafka.
6. La app móvil / panel web actualiza el Timeline de la Saga a estado verde consolidado: *"Liquidación Aprobada y Transferencia Autorizada"*.

### 3. Flujos Alternativos y Compensación Semántica (Rollback)
- **FA-09.1 (Rollback por Insuficiencia de Reserva o Falla Bancaria en Paso 3):**
  1. Si en el Paso 3 el cálculo actuarial determina que el fondo de reservas del ramo automotor es insuficiente, MS3 aborta el desembolso.
  2. MS3 inicia la **Compensación Semántica**: publica eventos en el tópico Kafka `aegiscore.saga.compensations`.
  3. **Reversión Paso 2:** Publica `CompensarCoberturaCommand`. MS1 (PHP) consume el comando y restituye el saldo de cobertura en la póliza.
  4. **Reversión Paso 1:** Publica `RevertirEstadoReclamoCommand`. MS2 (NestJS) consume el comando, ejecuta `RevertirEstadoReclamoHandler`, y devuelve el siniestro a `PERITAJE_COMPLETADO` con la nota de auditoría *"Liquidación revertida por fondos insuficientes"*.
  5. MS3 actualiza la saga a `COMPENSADA_FALLIDA` y emite `SagaLiquidacionFallidaCompensadaEvent`.
  6. La app móvil muestra en el Timeline la alerta roja con el paso exacto que falló y el detalle de la compensación ejecutada con éxito.

### 4. Trazabilidad ICONIX
- **Boundary:** `SagaTimelineScreen` (Flutter), `LiquidacionRestController` (Spring Boot), Tópicos Kafka (`aegiscore.saga.commands`, `events`, `compensations`).
- **Control:** `SagaLiquidacionOrchestratorService` (MS3 Hexagonal), `CalculoActuarialService` (Dominio Spring Boot), `MarcarEnLiquidacionHandler` y `RevertirEstadoReclamoHandler` (MS2 NestJS).
- **Entity:** `orden_liquidacion_saga` (PostgreSQL MS3), `expedientes_siniestros` (MongoDB MS2), `polizas` (PostgreSQL MS1).

---

## 💳 CU10: Procesar Cobro Recurrente de Primas y Pago QR Idempotente

### 1. Ficha Técnica
| Atributo | Detalle |
|---|---|
| **Identificador** | `CU10` |
| **Nombre** | Generar y procesar cobros de primas de seguro mediante códigos QR estándar con garantía de idempotencia financiera en DynamoDB. |
| **Actor Primario** | Asegurado / Pasarela Bancaria QR. |
| **Disparador** | El asegurado procede a pagar su cuota mensual de seguro escaneando o generando un código QR en su dispositivo. |
| **Precondiciones** | La póliza tiene cuotas pendientes de cobro y el cliente cuenta con saldo en su billetera digital o aplicación bancaria. |
| **Postcondiciones** | Se registra la transacción financiera en PostgreSQL, se emite el comprobante de pago digital y se adquiere el candado de no duplicación en DynamoDB. |

### 2. Flujo Principal (Happy Path)
1. El asegurado accede a **"CU10: Cobros y Pagos QR Idempotentes"** en la app móvil.
2. La app presenta el detalle de la prima adeudada (ej. *150,00 BOB*) y genera el código QR estándar EMV/BCB codificado en base64.
3. El asegurado simula la confirmación bancaria del pago pulsando **"CONFIRMAR PAGO QR CON IDEMPOTENCIA"**.
4. La app genera un `Idempotency-Key` (UUIDv4) único para la transacción bancaria.
5. Emite la solicitud `POST /api/v1/cobranzas/qr/confirmar` hacia MS3 (Spring Boot 3 - Arquitectura Hexagonal).
6. El adaptador `DynamoDbIdempotencyAdapter` verifica contra la tabla `IdempotencyRecords` de DynamoDB Local.
7. Al ser una clave nueva, adquiere el bloqueo transaccional (`status = PROCESSING`).
8. El puerto de entrada `ProcesarPagoPrimaQRUseCasePort` y su implementación `CobranzaPrimaQRService` procesan el cobro.
9. El adaptador JPA `PostgreSqlPagoPrimaAdapter` inserta el asiento contable en la tabla `pago_prima` de PostgreSQL.
10. Se actualiza el registro en DynamoDB con estado `COMPLETED` y el identificador de recibo bancario (`RECIBO-QR-2026-XXXX`).
11. La app móvil renderiza la confirmación de transacción aprobada con su código de recibo, sellado de tiempo y badge de no duplicidad financiera.

### 3. Flujos Alternativos y Excepciones
- **FA-10.1 (Doble click del asegurado o reintento de pasarela):** Si la pasarela o el cliente pulsa el botón dos veces por lentitud de conexión, DynamoDB intercepta la segunda petición por la misma clave, detecta el estado `COMPLETED` y devuelve de inmediato el recibo ya procesado con código HTTP 200 sin volver a debitar fondos ni insertar asientos duplicados en la base de datos contable.
- **EX-10.1 (Pago sobre cuota ya liquidada):** Si la cuota fue saldada previamente por otro canal, el servicio bancario rechaza la operación con código HTTP 422.

### 4. Trazabilidad ICONIX
- **Boundary:** `QrPaymentScreen` (Flutter UI & QR Generator), `PagoQRRestController` (Spring Boot REST).
- **Control:** `CobranzaPrimaQRService` (Spring Boot Hexagonal Inbound Port), `DynamoDbIdempotencyAdapter`, `IdempotencyService`.
- **Entity:** `pago_prima` (PostgreSQL 16), `IdempotencyRecords` (DynamoDB Local), `TransaccionPagoQR` (Entidad de dominio puro).

