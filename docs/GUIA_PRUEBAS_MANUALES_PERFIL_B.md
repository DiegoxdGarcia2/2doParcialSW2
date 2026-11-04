# 🧪 Guía Oficial de Pruebas Manuales y Defensa — AegisCore AI (Perfil B)
> **Materia:** Ingeniería de Software II (2do Parcial) — **Grupo:** #27  
> **Célula B:** Siniestros, Movilidad en Terreno 100% Offline, Idempotencia Distribuida & Transacción Saga  
> **Casos de Uso a Cargo:** CU06, CU07, CU08, CU09 y CU10  

---

## 🚀 1. Estado de Servicios y Conectividad para la Defensa

Para ejecutar las pruebas en vivo o defender ante el docente, los servicios se organizan en la siguiente topología:

| Componente | Servicio / Framework | Puerto | Protocolo / Rol | Estado |
|---|---|---|---|---|
| **App Móvil** | Flutter 3.x (Android Físico / Emulador) | Dispositivo | SQLite Local + TFLite On-Device | 🟢 **INSTALADA** |
| **MS2 Siniestros** | NestJS 10 (Clean Architecture + CQRS) | `8002` | [http://localhost:8002/health](http://localhost:8002/health) · MongoDB | 🟢 **UP** |
| **MS3 Actuarial** | Spring Boot 3 (Arquitectura Hexagonal) | `8003` | [http://localhost:8003/actuator/health](http://localhost:8003/actuator/health) · PostgreSQL | 🟢 **UP** |
| **DynamoDB Local** | Amazon DynamoDB Local Container | `8000` | Clave-Valor (`AegisCore_IdempotencyRecords`) | 🟢 **UP** |
| **MongoDB 7** | Mongo Container (`aegiscore_siniestros`) | `27017` | NoSQL Documental (`2dsphere` GPS) | 🟢 **UP** |
| **PostgreSQL 16** | Postgres Container (`aegiscore_erp`) | `5432` | Relacional ACID (Saga, Pagos QR) | 🟢 **UP** |
| **Túnel USB ADB** | `adb reverse tcp:8002 tcp:8002` | `8002/8003` | Puente celular $\leftrightarrow$ PC sin requerir Wi-Fi | 🟢 **ENLAZADO** |

---

## 🔌 2. Configuración de Conexión del Teléfono Móvil

### Opción A: Teléfono Físico con Cable USB (Recomendado)
Tu celular físico se comunica con los microservicios de tu computadora directamente por el cable USB sin depender de router o señal Wi-Fi:
```powershell
# Verificar dispositivo conectado
adb devices

# Habilitar el túnel inverso
adb reverse tcp:8002 tcp:8002
adb reverse tcp:8003 tcp:8003
```
*En la app, la IP por defecto es **`127.0.0.1`**.*

### Opción B: Teléfono en Misma Red Wi-Fi (Inalámbrico)
Si desconectas el cable USB:
1. En la app móvil, toca el icono de red `[ <·> ]` en la barra superior.
2. Selecciona el chip **`192.168.1.148 (Wi-Fi)`** y pulsa **GUARDAR**.

---

## 🔬 3. Batería de Pruebas Manuales Paso a Paso (Demostración al Docente)

---

### 🚨 PRUEBA 1 — CU06: Reportar Siniestro Vial de Emergencia SOS con Triaje
- **Objetivo:** Demostrar la recepción de un reclamo urgente desde el móvil con telemetría GPS, triaje automático e inserción geoespacial en MongoDB.
- **Pasos a seguir:**
  1. En el menú principal de la App Flutter, ingresa a **"CU06: Reporte SOS de Emergencia"**.
  2. Observa cómo la app captura automáticamente las coordenadas satelitales (Latitud / Longitud).
  3. Marca las condiciones de la colisión:
     - Lesionados: `0`
     - Vehículo inmovilizado: `Activado`
     - Airbags desplegados: `Desactivado`
     - Descripción: *"Colisión por alcance en intersección con semáforo intermitente."*
  4. Pulsa el botón rojo principal: **`[ 🚨 EMITIR ALERTA SOS INMEDIATA ]`**.
- **Qué verificar:**
  - En la app: Aparece el cuadro de confirmación con el número de reclamo generado y la severidad calculada (`MODERADO`).
  - En MongoDB (Terminal PC):
    ```powershell
    docker exec -it aegiscore-mongo-siniestros mongosh aegiscore_siniestros --eval "db.expedientes_siniestros.find().sort({_id:-1}).limit(1).pretty()"
    ```
    Comprueba que el documento tiene coordenadas GeoJSON y estado `REPORTADO` o `EN_TRIAJE`.

---

### 📱 PRUEBA 2 — CU07: Inspección de Daños 100% Offline con Edge AI (TFLite)
- **Objetivo:** Demostrar que el perito puede inspeccionar un choque en una carretera o sótano sin señal de internet, clasificando piezas con una red neuronal local y guardando en SQLite.
- **Pasos para simular falta total de internet:**
  1. *(Opcional para impactar al docente)*: Pon tu teléfono celular en **Modo Avión** o desactiva los datos móviles y Wi-Fi.
  2. En la app, entra a **"CU07: Peritaje Offline + Edge AI (TFLite)"**.
  3. Número de Reclamo: Mantén `REC-2026-00050` o escribe uno nuevo.
  4. Selecciona la pieza a evaluar: `Parachoques` (o `Capó` / `Faroles`).
  5. Pulsa el botón: **`[ 🧠 EVALUAR PIEZA CON EDGE AI (TFLITE) ]`**.
  6. Observa el diagnóstico en pantalla:
     - Modelo de inferencia local: Cuantizado `damage_classifier.tflite` (LiteRT).
     - Confianza IA: $\approx 88\% - 95\%$.
     - Presupuesto sugerido de repuesto y mano de obra: `1.200,00 BOB`.
  7. Pulsa el botón inferior: **`[ 💾 GUARDAR PERITAJE EN SQLITE LOCAL (OFFLINE) ]`**.
- **Qué verificar:**
  - Aparece la alerta verde: *"Peritaje Guardado Localmente en SQLite (100% Offline)"*.
  - Los datos están en disco físico del celular protegidos con Hash SHA-256 e Idempotency-Key UUIDv4, **sin haber necesitado conexión a ningún servidor**.

---

### 🔄 PRUEBA 3 — CU08: Sincronización Idempotente con DynamoDB (<5 ms)
- **Objetivo:** Demostrar que al recuperar conectividad, la cola se sincroniza y DynamoDB protege contra reintentos duplicados por mala señal.
- **Pasos a seguir:**
  1. Desactiva el modo avión (si lo activaste) y reconecta el cable USB.
  2. En la app, entra a **"CU08: Sincronización Idempotente (DynamoDB)"**.
  3. Verás la tarjeta pendiente en la pestaña **"En Cola SQLite (1)"** con su monto (`1.200,00 BOB`), su clave UUIDv4 y su Hash SHA-256.
  4. Pulsa el botón: **`[ 🔄 SINCRONIZAR COLA CON MS2 Y DYNAMODB ]`**.
  5. **Primer Intento (Creación):**
     - La tarjeta desaparece de la cola y pasa a la pestaña **"Sincronizados (1)"** con badge verde `SINCRONIZADO EN NUBE`.
     - MongoDB recibe el peritaje y transiciona el siniestro a `PERITAJE_COMPLETADO`.
  6. **Segundo Intento (Simulación de reintento con misma clave):**
     - Si vuelves a pulsar sincronizar con esa misma clave o ejecutas la prueba de estrés:
     - DynamoDB detecta `status = COMPLETED` y responde en **menos de 25 ms** con la cabecera:
       ```http
       X-Cache-Lookup: HIT_IDEMPOTENCY_DYNAMODB
       ```
- **Qué verificar en DynamoDB (Terminal PC):**
  ```powershell
  node -e "const { DynamoDBClient, ScanCommand } = require('./backend/ms2-siniestros-nestjs/node_modules/@aws-sdk/client-dynamodb'); const client = new DynamoDBClient({ endpoint: 'http://127.0.0.1:8000', region: 'us-east-1', credentials: { accessKeyId: 'local', secretAccessKey: 'local' } }); client.send(new ScanCommand({ TableName: 'AegisCore_IdempotencyRecords' })).then(r => console.log('Total registros:', r.Items.length));"
  ```
  El registro de tu siniestro aparece con status `COMPLETED` y `http_status_code: 200`.

---

### ⚖️ PRUEBA 4 — CU09: Orquestación Saga en 3 Microservicios con Rollback Kafka
- **Objetivo:** Demostrar la transacción distribuida transversal coordinada por MS3 Spring Boot entre MS2 (NestJS), MS1 (PHP) y MS3 (Spring Boot), con su compensación semántica si falla el fondo actuarial.
- **Pasos a seguir:**
  1. En la app móvil, abre **"CU09: Transacción Transversal Saga (3 MS)"**.
  2. Verás el **Timeline interactivo de la Saga de Liquidación**:
     - *Paso 1:* MS2 NestJS $\rightarrow$ Bloqueo de Reclamo (`EN_PROCESO_LIQUIDACION`).
     - *Paso 2:* MS1 PHP $\rightarrow$ Débito de Cobertura en Póliza.
     - *Paso 3:* MS3 Spring Boot $\rightarrow$ Verificación de Reserva Actuarial y Asiento Contable.
  3. Pulsa **`[ ▶️ AVANZAR PASO DE LA SAGA ]`** para ver la transición exitosa de estados.
  4. Pulsa **`[ ⚠️ SIMULAR FALLO EN PASO 3 Y COMPENSACIÓN (ROLLBACK) ]`**:
     - Se simula una caída en el fondo de reserva o rechazo bancario.
     - Observa cómo se emiten los comandos compensatorios en Kafka hacia el tópico `aegiscore.saga.compensations`:
       - `CompensarCoberturaCommand`: MS1 restituye el saldo de cobertura.
       - `RevertirEstadoReclamoCommand`: MS2 devuelve el siniestro a `PERITAJE_COMPLETADO`.
     - El timeline resalta la ruta de reversión en color carmesí de auditoría.
- **Qué verificar en MS3 Spring Boot:**
  Las pruebas unitarias de la Saga y su compensación pasan al 100%:
  ```powershell
  $env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"; cd backend\ms3-actuarial-springboot; .\mvnw.cmd test -Dtest=SagaLiquidacionOrchestratorServiceTest
  ```

---

### 💳 PRUEBA 5 — CU10: Cobros y Pagos QR Idempotentes
- **Objetivo:** Demostrar el procesamiento de cobro recurrente de pólizas mediante código QR con blindaje contra pagos duplicados en MS3 Spring Boot.
- **Pasos a seguir:**
  1. En la app móvil, abre **"CU10: Cobros y Pagos QR Idempotentes"**.
  2. Verás el código QR oficial renderizado en pantalla (Monto: `150,00 BOB` - Cuota Mensual Póliza).
  3. Pulsa **`[ 💳 CONFIRMAR PAGO QR CON IDEMPOTENCIA ]`**.
  4. La app despacha la solicitud con `Idempotency-Key` (UUIDv4) hacia MS3 Spring Boot (`POST /api/v1/cobranzas/qr/confirmar`).
  5. Aparece la tarjeta de confirmación bancaria:
     - Estado: `PAGO_CONFIRMADO`
     - Recibo: `RECIBO-QR-2026-XXXX`
     - Registro contable asentado en PostgreSQL `pago_prima`.
  6. *(Prueba de doble click)*: Si se reintenta el cobro con la misma clave, MS3 detecta el lock en DynamoDB y responde de inmediato con el recibo existente sin debitar dos veces la prima.

---

## 🎓 4. Guía y Argumentación para la Defensa Oral ante el Docente

| Pregunta Trampa del Docente | Respuesta y Justificación Técnica de Alto Nivel |
|---|---|
| **1. ¿Por qué aplicaron Clean Architecture en NestJS y Arquitectura Hexagonal en Spring Boot en lugar del mismo patrón?** | *"Para demostrar versatilidad y apego estricto a las exigencias arquitectónicas. En **MS2 NestJS** usamos **Clean Architecture con CQRS**, aislando el dominio de Mongoose y dividiendo comandos que mutan de queries de solo lectura. En **MS3 Spring Boot** usamos **Arquitectura Hexagonal (Ports & Adapters)**, donde los puertos de entrada modelan casos de uso actuariales puros y los puertos de salida desacoplan la base de datos relacional y el broker Kafka."* |
| **2. ¿Por qué usar Amazon DynamoDB para Idempotencia en vez de una simple tabla en PostgreSQL o MongoDB?** | *"Por latencia y concurrencia crítica. La verificación de idempotencia debe resolverse en **sub-milisegundos (< 5 ms)** en cada petición HTTP. Un motor relacional como Postgres crearía contención de locks en transacciones concurrentes, y MongoDB sobrecargaría escrituras. DynamoDB Local (NoSQL Clave-Valor) ofrece consultas $O(1)$ por Partition Key inmediatas y soporte nativo de TTL."* |
| **3. ¿Cómo aseguran consistencia en la liquidación si se cae la red o el microservicio 3 a mitad de camino?** | *"Mediante una **Transacción Distribuida con Patrón Saga Orquestada**. Si en el Paso 3 MS3 detecta fondos actuariales insuficientes o error bancario, no puede hacer un ROLLBACK SQL tradicional porque son 3 bases de datos independientes. Por ello, publica eventos compensatorios en el tópico Kafka `aegiscore.saga.compensations`, ordenando a MS1 restituir el saldo y a MS2 revertir el reclamo en orden inverso."* |
| **4. ¿Por qué la app móvil funciona sin internet y cómo sabe qué parte del auto está rota sin consultar a la nube?** | *"Implementamos **Edge AI (IA en el dispositivo)**. Cuantizamos el modelo de visión convolucional a **TensorFlow Lite (.tflite)** para que la inferencia de tensores corra en la CPU/NPU local del celular. La captura pericial, fotos y el Idempotency-Key se guardan atómicamente en **SQLite local**, garantizando operación en carreteras o sótanos sin señal."* |

