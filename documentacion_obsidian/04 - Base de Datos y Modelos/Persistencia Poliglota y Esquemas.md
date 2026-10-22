# 💾 Persistencia Políglota y Esquemas Físicos

## 1. PostgreSQL 16 (`aegiscore_erp`)
- **Tablas:**
  - `usuario`: Clientes, administradores y peritos enlazados al `sub` de Keycloak.
  - `cliente`: Registro de asegurados con perfil de riesgo y score crediticio.
  - `plan_seguro` y `cobertura`: Catálogo comercial de pólizas.
  - `poliza`: Aggregate Root en DDD con saldo de cobertura restante y JSONB de vehículos.
  - `factura_nota_venta`: Emisión fiscal/comercial en PDF con hash SHA-256.
  - `pago_prima`: Cobros QR idempotentes con clave UUIDv4.
  - `orden_liquidacion_saga`: Estados del orquestador transversal Saga en MS3 Spring Boot.
  - `reserva_tecnica`: Fondos de solvencia actuarial.
  - `dataset_historico_ml_polizas`: 1,200 registros sintéticos históricos para entrenamiento de Random Forest (CU12).

## 2. MongoDB 7 (`aegiscore_siniestros`)
- **Colecciones:**
  - `expedientes_siniestros`: Validación JSON Schema, índice geoespacial `2dsphere` e índice único en `numero_reclamo`.
  - `peritajes_ia_vision`: Inferencia de daños y severidad estructural por TensorFlow/Keras.
  - `bitacora_agente_autonomo`: Historial de ejecución de metas y habilidades de LangGraph.
  - `alertas_fraude_anomalias`: Resultados del modelo Isolation Forest.

## 3. Amazon DynamoDB Local
- **Tablas:**
  - `IdempotencyRecords`: Partition Key `idempotency_key` (UUIDv4) con TTL y cache de respuesta para latencia < 5ms.
  - `SesionesSSO`: Partition Key `session_id` con TTL para control rápido de tokens JWT.
