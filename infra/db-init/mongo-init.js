/**
 * =============================================================================
 *  AEGISCORE AI - Script de Inicialización de MongoDB 7
 *  Base de Datos: aegiscore_siniestros
 *  Microservicios conectados:
 *    - ms2-siniestros-nestjs (Clean Architecture + CQRS) -> Expedientes y Triaje
 *    - ms4-ia-mcp-python (TensorFlow, Agentes LangGraph, MCP) -> Peritajes y Logs
 * =============================================================================
 */

const dbName = 'aegiscore_siniestros';
const dbInstance = db.getSiblingDB(dbName);

print(`[*] Inicializando base de datos MongoDB: ${dbName}`);

// =============================================================================
// 1. COLECCIÓN: expedientes_siniestros (Validación JSON Schema + Índices)
// =============================================================================
dbInstance.createCollection('expedientes_siniestros', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['numero_reclamo', 'poliza_id', 'estado', 'tipo_siniestro'],
      properties: {
        numero_reclamo: {
          bsonType: 'string',
          description: 'Identificador único del expediente (ej. REC-2026-00101)'
        },
        poliza_id: {
          bsonType: 'string',
          description: 'UUID de la póliza en PostgreSQL'
        },
        numero_poliza: {
          bsonType: 'string',
          description: 'Número visible de póliza'
        },
        estado: {
          enum: [
            'REPORTADO',
            'EN_REVISION_IA',
            'ASIGNADO_PERITO',
            'PERITAJE_COMPLETADO',
            'EN_PROCESO_LIQUIDACION',
            'OBSERVADO_FINANZAS',
            'LIQUIDADO',
            'RECHAZADO'
          ],
          description: 'Estado del ciclo de vida del siniestro'
        },
        tipo_siniestro: {
          enum: ['CHOQUE_VIAL', 'ROBO_PARCIAL', 'ROBO_TOTAL', 'EMERGENCIA_MEDICA', 'VUELCO'],
          description: 'Categoría del siniestro'
        },
        geolocalizacion: {
          bsonType: 'object',
          required: ['type', 'coordinates'],
          properties: {
            type: { enum: ['Point'] },
            coordinates: {
              bsonType: 'array',
              minItems: 2,
              maxItems: 2,
              items: { bsonType: ['double', 'int'] },
              description: '[longitud, latitud]'
            }
          }
        },
        idempotency_key: {
          bsonType: 'string',
          description: 'UUIDv4 enviado desde la app móvil o web para control contra DynamoDB'
        },
        monto_estimado_reparacion: {
          bsonType: ['double', 'int', 'decimal'],
          description: 'Monto estimado preliminar en USD'
        },
        monto_indemnizacion_aprobado: {
          bsonType: ['double', 'int', 'decimal'],
          description: 'Monto aprobado para la liquidación Saga en USD'
        }
      }
    }
  }
});

// Índices optimizados
dbInstance.expedientes_siniestros.createIndex({ numero_reclamo: 1 }, { unique: true });
dbInstance.expedientes_siniestros.createIndex({ poliza_id: 1 });
dbInstance.expedientes_siniestros.createIndex({ estado: 1 });
dbInstance.expedientes_siniestros.createIndex({ idempotency_key: 1 }, { sparse: true });
dbInstance.expedientes_siniestros.createIndex({ geolocalizacion: '2dsphere' }); // Para reasignación de peritos por proximidad GPS (CU14)
dbInstance.expedientes_siniestros.createIndex({ created_at: -1 });

// =============================================================================
// 2. COLECCIÓN: peritajes_ia_vision (Inferencia de Redes Convolucionales TF/Keras)
// =============================================================================
dbInstance.createCollection('peritajes_ia_vision');
dbInstance.peritajes_ia_vision.createIndex({ expediente_id: 1 });
dbInstance.peritajes_ia_vision.createIndex({ fecha_analisis: -1 });

// =============================================================================
// 3. COLECCIÓN: bitacora_agente_autonomo (Logs de LangGraph con Metas y Habilidades)
// =============================================================================
dbInstance.createCollection('bitacora_agente_autonomo');
dbInstance.bitacora_agente_autonomo.createIndex({ meta_ejecutada: 1 });
dbInstance.bitacora_agente_autonomo.createIndex({ timestamp: -1 });

// =============================================================================
// 4. COLECCIÓN: alertas_fraude_anomalias (Resultados de Isolation Forest)
// =============================================================================
dbInstance.createCollection('alertas_fraude_anomalias');
dbInstance.alertas_fraude_anomalias.createIndex({ reclamo_id: 1 });
dbInstance.alertas_fraude_anomalias.createIndex({ score_anomalia: -1 });

// =============================================================================
// DATOS SEMILLA / DEMOSTRATIVOS (Siniestro inicial listo para probar Saga CU09)
// =============================================================================
const expedienteDemoId = new ObjectId();

dbInstance.expedientes_siniestros.insertOne({
  _id: expedienteDemoId,
  numero_reclamo: 'REC-2026-00492',
  poliza_id: 'd0000001-0000-0000-0000-000000000001',
  numero_poliza: 'POL-2026-AUT-00892',
  estado: 'PERITAJE_COMPLETADO', // Listo para que CU09 lo marque en EN_PROCESO_LIQUIDACION
  tipo_siniestro: 'CHOQUE_VIAL',
  descripcion: 'Colisión por alcance frontal en intersección con semáforo intermitente.',
  canal_origen: 'WHATSAPP_N8N',
  idempotency_key: '9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d',
  geolocalizacion: {
    type: 'Point',
    coordinates: [-63.1812, -17.7833] // Santa Cruz de la Sierra, Bolivia
  },
  ubicacion_texto: '4to Anillo y Av. San Martín, Equipetrol Norte',
  triaje_ia: {
    gravedad: 'MEDIA',
    score_danos: 0.74,
    piezas_detectadas: ['PARACHOQUES_DELANTERO', 'OPTICA_DERECHA', 'CAPO_PARCIAL'],
    modelo_inferencia: 'TensorFlow-YOLO-CrashNet-v2.1'
  },
  peritaje_campo: {
    perito_id: 'u0000001-0000-0000-0000-000000000002',
    perito_nombre: 'Ing. Roberto Paz',
    fecha_inspeccion: new Date(),
    ocr_placa_detectada: '4028-PLK',
    coincide_con_poliza: true,
    agente_tflite_valido: true,
    notas: 'Estructura chasis intacta. Radiador sin fuga visible. Reemplazo de ópticas y enderezado de capó requerido.'
  },
  fotos_evidencia: [
    {
      url: 'https://storage.aegiscore.local/evidencias/rec-00492-frente.jpg',
      categoria: 'ANGULO_FRONTAL',
      nitidez_score: 0.94,
      es_valido_tfjs: true
    },
    {
      url: 'https://storage.aegiscore.local/evidencias/rec-00492-lateral.jpg',
      categoria: 'ANGULO_LATERAL_DERECHO',
      nitidez_score: 0.89,
      es_valido_tfjs: true
    }
  ],
  monto_estimado_reparacion: 2850.00,
  monto_indemnizacion_aprobado: 2500.00, // Monto a liquidar en la Saga
  deducible_calculado: 250.00,
  created_at: new Date(Date.now() - 3600 * 24 * 1000 * 2), // Hace 2 días
  updated_at: new Date()
});

dbInstance.peritajes_ia_vision.insertOne({
  expediente_id: expedienteDemoId,
  numero_reclamo: 'REC-2026-00492',
  fecha_analisis: new Date(),
  piezas_analizadas: [
    { pieza: 'PARACHOQUES_DELANTERO', probabilidad: 0.96, severidad_porcentaje: 85, accion_sugerida: 'REEMPLAZO' },
    { pieza: 'FAROL_DELANTERO_DER', probabilidad: 0.92, severidad_porcentaje: 100, accion_sugerida: 'REEMPLAZO' },
    { pieza: 'CAPO', probabilidad: 0.88, severidad_porcentaje: 35, accion_sugerida: 'ENDEREZADO_PINTURA' }
  ],
  severidad_global: 'MEDIA',
  costo_estimado_taller_usd: 2850.00,
  modelo_tf_version: 'aegiscore-crash-detection-2026.keras'
});

dbInstance.bitacora_agente_autonomo.insertOne({
  timestamp: new Date(),
  meta_ejecutada: 'META_1_EVITAR_CUELLOS_BOTELLA_SINIESTROS',
  skill_utilizada: 'SKILL_REASIGNAR_PERITO_GPS',
  detalles: {
    expediente_numero: 'REC-2026-00492',
    tiempo_espera_minutos: 16,
    perito_asignado: 'Ing. Roberto Paz',
    distancia_km: 2.4
  },
  resultado: 'EXITOSO'
});

print('[OK] MongoDB aegiscore_siniestros inicializado con esquemas, índices y datos demo.');
