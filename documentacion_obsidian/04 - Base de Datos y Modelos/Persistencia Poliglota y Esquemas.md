# 💾 Persistencia Políglota y Esquemas Físicos (Cloud Ready)

## 1. Neon Serverless PostgreSQL (`neondb` / AWS us-east-2)
- **Host:** `ep-damp-salad-b5enofaj-pooler.c-7.us-east-2.aws.neon.tech` (SSL `require`)
- **Microservicios Conectados:**
  - `ms1-polizas-php` (PHP 8.3 / Laravel DDD via `config/database.php`)
  - `ms3-actuarial-springboot` (Java 21 / Spring Boot 3 Hexagonal via `application.yml` + HikariCP)
  - `ms4-ia-mcp-python` (Python 3.11 / FastAPI via `app/db/connections.py` para Random Forest y MCP)
- **Tablas Creadas y Operativas (10):**
  - `usuario`: Clientes, administradores y peritos enlazados al `sub` de Keycloak.
  - `cliente`: Registro de asegurados con perfil de riesgo y score crediticio.
  - `plan_seguro` y `cobertura`: Catálogo comercial de pólizas.
  - `poliza`: Aggregate Root en DDD con saldo de cobertura restante y JSONB de vehículos.
  - `factura_nota_venta`: Emisión fiscal/comercial en PDF con hash SHA-256.
  - `pago_prima`: Cobros QR idempotentes con clave UUIDv4.
  - `orden_liquidacion_saga`: Estados del orquestador transversal Saga en MS3 Spring Boot.
  - `reserva_tecnica`: Fondos de solvencia actuarial.
  - `dataset_historico_ml_polizas`: **1,200 registros sintéticos históricos** para entrenamiento y validación de Random Forest (CU12) y K-Means (CU13).

## 2. MongoDB Atlas Cloud (`aegiscore_siniestros_db` / Cluster AWS)
- **Cluster:** `cluster0.t4wz787.mongodb.net`
- **Microservicios Conectados:**
  - `ms2-siniestros-nestjs` (NestJS 10 Clean Architecture via `MongooseModule.forRoot`)
  - `ms4-ia-mcp-python` (FastAPI via `pymongo.MongoClient` para inferencia TF y agentes)
- **Colecciones e Índices Activos (4):**
  - `expedientes_siniestros`: Validación BSON, índice geoespacial `2dsphere` (para proximidad GPS CU14), índice único en `numero_reclamo`, e índice `idempotency_key`.
  - `peritajes_ia_vision`: Inferencia de daños y severidad estructural por TensorFlow/Keras con índice temporal.
  - `bitacora_agente_autonomo`: Historial de ejecución de metas y habilidades de LangGraph.
  - `alertas_fraude_anomalias`: Resultados del modelo Isolation Forest.

## 3. Amazon DynamoDB Cloud (`us-east-2`)
- **Tabla:** `AegisCore_IdempotencyRecords`
- **Partition Key:** `idempotencyKey` (String, UUIDv4)
- **TTL:** Activo (`ENABLED`) en atributo `expiresAt`
- **Microservicios Conectados:**
  - `ms2-siniestros-nestjs` (`DynamoIdempotencyRepository` con `@aws-sdk/client-dynamodb` y `@aws-sdk/lib-dynamodb`)
  - `ms3-actuarial-springboot` (Validación de idempotencia en Saga CU09)
  - `ms4-ia-mcp-python` (`get_idempotency_table()` con `boto3`)
- **Latencia:** Sub-5ms para evitar doble cobro (CU10) y duplicación de reclamos ante mala señal (CU08).

## 4. Scripts Operativos de Verificación
- `scripts/verify_cloud_dbs.py`: Chequeo de salud instantáneo de los 3 motores cloud con visualización de estado.
- `scripts/seed_cloud_dbs.py`: Poblado y verificación de integridad DDL, colecciones, índices y datasets sintéticos.
