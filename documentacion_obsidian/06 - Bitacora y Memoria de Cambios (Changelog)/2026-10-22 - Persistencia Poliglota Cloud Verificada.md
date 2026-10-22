# 🚀 Bitácora: Configuración y Verificación de Persistencia Políglota Cloud (100% Operativa)

- **Fecha:** 2026-10-22
- **Autor / Agente:** Arquitecto de Software & Ingeniero Backend Senior
- **Estado:** ✅ Verificado y en producción cloud

---

## 📌 Resumen de la Tarea
Se configuraron las credenciales definitivas y clientes de conexión a las 3 bases de datos en la nube (Neon Serverless PostgreSQL, MongoDB Atlas Cloud y Amazon DynamoDB Cloud en `us-east-2`), aplicando los patrones arquitectónicos exigidos para cada microservicio.

---

## 🏛️ Adaptación por Microservicio
1. **`backend/ms1-polizas-php` (Laravel DDD):**
   - Archivo: `config/database.php`
   - Configurado con driver PostgreSQL para Neon Serverless con `sslmode => 'require'`, charset UTF-8 y lectura desde `DATABASE_URL`.
   - Endpoint: `/health/db` para diagnóstico inmediato.

2. **`backend/ms2-siniestros-nestjs` (NestJS Clean Architecture + CQRS):**
   - Conexión MongoDB Atlas via `MongooseModule.forRoot` en `AppModule`.
   - Repositorio `DynamoIdempotencyRepository` implementado con `@aws-sdk/client-dynamodb` y `@aws-sdk/lib-dynamodb` sobre la tabla `AegisCore_IdempotencyRecords`.
   - Controlador `HealthController` con `/health/cloud-dbs` para monitoreo de estado.

3. **`backend/ms3-actuarial-springboot` (Spring Boot 3 - Arquitectura Hexagonal):**
   - Archivo: `src/main/resources/application.yml`
   - Conexión JDBC a Neon PostgreSQL con driver `org.postgresql.Driver` y pooling HikariCP (`maximum-pool-size: 10`, `connection-test-query: SELECT 1`).
   - Configuración de credenciales AWS para soporte de idempotencia en Saga transversal.

4. **`backend/ms4-ia-mcp-python` (FastAPI / Pipelines IA + Servidor MCP):**
   - Archivo: `app/db/connections.py`
   - Clientes `pymongo.MongoClient` (MongoDB Atlas), `boto3.resource('dynamodb')` (DynamoDB) y `psycopg2` (Neon).
   - Endpoint `/health/cloud-dbs` retornando `"status": "ALL_HEALTHY"`.

---

## 📊 Poblado y Verificación Físico-Lógica
- **Neon PostgreSQL:**
  - Esquema DDL ejecutado: 10 tablas creadas (`usuario`, `cliente`, `plan_seguro`, `cobertura`, `poliza`, `factura_nota_venta`, `pago_prima`, `orden_liquidacion_saga`, `reserva_tecnica`, `dataset_historico_ml_polizas`).
  - Dataset sintético para ML (CU12 Random Forest & CU13 K-Means): **1,200 registros generados exitosamente**.
  - Datos semilla creados para usuarios administradores, actuarios, peritos y póliza activa de prueba.
- **MongoDB Atlas:**
  - Colecciones creadas: `expedientes_siniestros`, `peritajes_ia_vision`, `bitacora_agente_autonomo`, `alertas_fraude_anomalias`.
  - Índice geoespacial `2dsphere` creado para reasignación de peritos por GPS (CU14).
  - Expediente demo inicial `REC-2026-00492` insertado con peritaje IA asociado.
- **Amazon DynamoDB Cloud (`us-east-2`):**
  - Tabla `AegisCore_IdempotencyRecords`: Estado `ACTIVE`, Partition Key `idempotencyKey`.
  - TTL verificado y habilitado (`ENABLED` en `expiresAt`).
  - Pruebas de `PutItem` y `GetItem` completadas satisfactoriamente.

---

## 🛠️ Herramientas Entregadas
- `scripts/verify_cloud_dbs.py`: Verificación visual en consola de los 3 motores en la nube.
- `scripts/seed_cloud_dbs.py`: Inicializador idempotente de esquemas, colecciones y datasets.
