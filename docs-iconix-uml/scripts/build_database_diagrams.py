# -*- coding: utf-8 -*-
import sqlite3
import uuid

def get_guid():
    return f"{{{uuid.uuid4()}}}".upper()

def get_duid():
    return uuid.uuid4().hex[:8].upper()

conn = sqlite3.connect('AegisCore_AI.qea')
cur = conn.cursor()

# 1. Crear Paquetes para las 3 Bases de Datos
root_pkg_id = 2  # EA_Model_AegisCore_AI

packages = [
    (8, '06_DB_PostgreSQL_Relacional', root_pkg_id),
    (9, '07_DB_MongoDB_Documental', root_pkg_id),
    (10, '08_DB_DynamoDB_NoSQL', root_pkg_id)
]

for pid, name, parent in packages:
    cur.execute("INSERT OR REPLACE INTO t_package (Package_ID, Name, Parent_ID, ea_guid) VALUES (?, ?, ?, ?)",
                (pid, name, parent, get_guid()))
    cur.execute("INSERT OR REPLACE INTO t_object (Object_ID, Package_ID, Object_Type, Name, ea_guid) VALUES (?, ?, 'Package', ?, ?)",
                (pid + 500, parent, name, get_guid()))

# 2. Crear los 3 Diagramas
diagrams = [
    (31, 8, "Logical", "4.3.1. Base de Datos Relacional PostgreSQL 16 (aegiscore_erp)"),
    (32, 9, "Logical", "4.3.2. Base de Datos NoSQL Documental MongoDB 7.0 (aegiscore_siniestros)"),
    (33, 10, "Logical", "4.3.3. Base de Datos NoSQL Clave-Valor Amazon DynamoDB (IdempotencyRecords)")
]

# Eliminar objetos y diagramas previos de estas bases de datos si existen
cur.execute("DELETE FROM t_diagram WHERE Diagram_ID IN (31, 32, 33)")
cur.execute("DELETE FROM t_diagramobjects WHERE Diagram_ID IN (31, 32, 33)")
cur.execute("DELETE FROM t_diagramlinks WHERE DiagramID IN (31, 32, 33)")
cur.execute("DELETE FROM t_connector WHERE Start_Object_ID >= 200 AND Start_Object_ID <= 250")
cur.execute("DELETE FROM t_attribute WHERE Object_ID >= 200 AND Object_ID <= 250")
cur.execute("DELETE FROM t_object WHERE Object_ID >= 201 AND Object_ID <= 235")

for did, pid, dtype, dname in diagrams:
    cur.execute("INSERT OR REPLACE INTO t_diagram (Diagram_ID, Package_ID, Diagram_Type, Name, ea_guid, cx, cy) VALUES (?, ?, ?, ?, ?, 1800, 1200)",
                (did, pid, dtype, dname, get_guid()))

# Helper para añadir tablas/colecciones
def add_table(obj_id, pkg_id, name, stereotype, notes=""):
    cur.execute("""
        INSERT OR REPLACE INTO t_object (Object_ID, Package_ID, Object_Type, Name, Stereotype, Note, ea_guid)
        VALUES (?, ?, 'Class', ?, ?, ?, ?)
    """, (obj_id, pkg_id, name, stereotype, notes, get_guid()))

# Helper para añadir atributos / columnas
attr_counter = 2000
def add_attr(obj_id, name, data_type, pos):
    global attr_counter
    attr_counter += 1
    cur.execute("""
        INSERT INTO t_attribute (Object_ID, Name, Scope, Type, Pos, ID, ea_guid)
        VALUES (?, ?, 'Public', ?, ?, ?, ?)
    """, (obj_id, name, data_type, pos, attr_counter, get_guid()))

# Helper para layout en diagrama con coordenadas negativas correctas de Enterprise Architect
def add_dobj(diag_id, obj_id, l, t, r, b):
    duid = get_duid()
    obj_style = f"DUID={duid};BCol=-1;BFol=-1;LCol=-1;"
    cur.execute("""
        INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectLeft, RectTop, RectRight, RectBottom, ObjectStyle)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (diag_id, obj_id, l, -t, r, -b, obj_style))

# Helper para relaciones / FKs
conn_counter = 700
def add_rel(name, ctype, src_id, dst_id, diag_id, src_card=None, dst_card=None):
    global conn_counter
    conn_counter += 1
    cguid = get_guid()
    cur.execute("""
        INSERT INTO t_connector (Connector_ID, Name, Connector_Type, Start_Object_ID, End_Object_ID, SourceCard, DestCard, ea_guid)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (conn_counter, name, ctype, src_id, dst_id, src_card, dst_card, cguid))
    cur.execute("""
        INSERT INTO t_diagramlinks (DiagramID, ConnectorID, Geometry)
        VALUES (?, ?, 'EDGE=1;')
    """, (diag_id, conn_counter))


# =============================================================================
# MODELO 1: POSTGRESQL 16 (aegiscore_erp) - 9 Tablas con Atributos y FKs
# =============================================================================
# 1. usuario
add_table(201, 8, "usuario", "table", "Sincronizado con Keycloak SSO (CU01)")
add_attr(201, "id", "UUID [PK]", 1)
add_attr(201, "keycloak_sub", "VARCHAR(64) [UNIQUE]", 2)
add_attr(201, "email", "VARCHAR(150) [UNIQUE]", 3)
add_attr(201, "nombre_completo", "VARCHAR(200)", 4)
add_attr(201, "rol", "VARCHAR(50) [ADMIN, PERITO, ACTUARIO]", 5)
add_attr(201, "telefono", "VARCHAR(30)", 6)
add_attr(201, "activo", "BOOLEAN", 7)
add_attr(201, "created_at", "TIMESTAMPTZ", 8)

# 2. cliente
add_table(202, 8, "cliente", "table", "Asegurados / Tomadores de Póliza")
add_attr(202, "id", "UUID [PK]", 1)
add_attr(202, "usuario_id", "UUID [FK -> usuario.id]", 2)
add_attr(202, "tipo_documento", "VARCHAR(20) [CI, NIT, DNI]", 3)
add_attr(202, "numero_documento", "VARCHAR(40) [UNIQUE]", 4)
add_attr(202, "nombres", "VARCHAR(100)", 5)
add_attr(202, "apellidos", "VARCHAR(100)", 6)
add_attr(202, "email", "VARCHAR(150)", 7)
add_attr(202, "telefono", "VARCHAR(30)", 8)
add_attr(202, "score_crediticio", "INT [300-950]", 9)
add_attr(202, "perfil_riesgo", "VARCHAR(30) [BAJO, MODERADO, ALTO]", 10)

# 3. plan_seguro
add_table(203, 8, "plan_seguro", "table", "Catálogo de Planes")
add_attr(203, "id", "UUID [PK]", 1)
add_attr(203, "codigo", "VARCHAR(30) [UNIQUE]", 2)
add_attr(203, "nombre", "VARCHAR(120)", 3)
add_attr(203, "tipo", "VARCHAR(30) [VEHICULAR, SALUD, VIDA]", 4)
add_attr(203, "prima_base_anual", "NUMERIC(12,2)", 5)
add_attr(203, "deducible_base_porcentaje", "NUMERIC(5,2)", 6)
add_attr(203, "activo", "BOOLEAN", 7)

# 4. cobertura
add_table(204, 8, "cobertura", "table", "Detalle de Coberturas asociadas a Planes")
add_attr(204, "id", "UUID [PK]", 1)
add_attr(204, "plan_id", "UUID [FK -> plan_seguro.id]", 2)
add_attr(204, "codigo", "VARCHAR(40)", 3)
add_attr(204, "nombre", "VARCHAR(150)", 4)
add_attr(204, "suma_asegurada_max", "NUMERIC(14,2)", 5)
add_attr(204, "deducible_minimo", "NUMERIC(10,2)", 6)
add_attr(204, "obligatoria", "BOOLEAN", 7)

# 5. poliza
add_table(205, 8, "poliza", "table", "Contrato de Seguro (Aggregate Root MS1)")
add_attr(205, "id", "UUID [PK]", 1)
add_attr(205, "numero_poliza", "VARCHAR(50) [UNIQUE]", 2)
add_attr(205, "cliente_id", "UUID [FK -> cliente.id]", 3)
add_attr(205, "plan_id", "UUID [FK -> plan_seguro.id]", 4)
add_attr(205, "estado", "VARCHAR(30) [COTIZADA, EMITIDA, ACTIVA]", 5)
add_attr(205, "fecha_inicio", "DATE", 6)
add_attr(205, "fecha_fin", "DATE", 7)
add_attr(205, "prima_anual", "NUMERIC(12,2)", 8)
add_attr(205, "prima_mensual", "NUMERIC(12,2)", 9)
add_attr(205, "saldo_cobertura_restante", "NUMERIC(14,2)", 10)
add_attr(205, "datos_bien_asegurado", "JSONB [placa, vin, valor]", 11)
add_attr(205, "canal_venta", "VARCHAR(40) [WEB_REACT, N8N]", 12)

# 6. factura_nota_venta
add_table(206, 8, "factura_nota_venta", "table", "Emisión Fiscal / Comercial (CU05 n8n)")
add_attr(206, "id", "UUID [PK]", 1)
add_attr(206, "numero_factura", "VARCHAR(50) [UNIQUE]", 2)
add_attr(206, "poliza_id", "UUID [FK -> poliza.id]", 3)
add_attr(206, "cliente_id", "UUID [FK -> cliente.id]", 4)
add_attr(206, "tipo_comprobante", "VARCHAR(20) [FACTURA, NOTA_VENTA]", 5)
add_attr(206, "subtotal", "NUMERIC(12,2)", 6)
add_attr(206, "impuestos", "NUMERIC(12,2)", 7)
add_attr(206, "total", "NUMERIC(12,2)", 8)
add_attr(206, "estado", "VARCHAR(20) [EMITIDA, PAGADA]", 9)
add_attr(206, "url_pdf_almacenado", "VARCHAR(255)", 10)
add_attr(206, "hash_digital_sha256", "VARCHAR(64)", 11)

# 7. pago_prima
add_table(207, 8, "pago_prima", "table", "Cobros QR Idempotentes (CU10 Spring Boot)")
add_attr(207, "id", "UUID [PK]", 1)
add_attr(207, "poliza_id", "UUID [FK -> poliza.id]", 2)
add_attr(207, "numero_cuota", "INT", 3)
add_attr(207, "monto", "NUMERIC(12,2)", 4)
add_attr(207, "metodo_pago", "VARCHAR(30) [QR_SIMPLE]", 5)
add_attr(207, "idempotency_key", "VARCHAR(64) [UNIQUE DynamoDB]", 6)
add_attr(207, "codigo_autorizacion_bancaria", "VARCHAR(80)", 7)
add_attr(207, "estado", "VARCHAR(20) [PENDIENTE, EXITOSO]", 8)
add_attr(207, "fecha_pago", "TIMESTAMPTZ", 9)

# 8. orden_liquidacion_saga
add_table(208, 8, "orden_liquidacion_saga", "table", "Orquestador Saga Transversal (CU09)")
add_attr(208, "id", "UUID [PK]", 1)
add_attr(208, "saga_id", "VARCHAR(64) [UNIQUE]", 2)
add_attr(208, "reclamo_id_mongo", "VARCHAR(64) [Ref MongoDB]", 3)
add_attr(208, "poliza_id", "UUID [FK -> poliza.id]", 4)
add_attr(208, "cliente_id", "UUID [FK -> cliente.id]", 5)
add_attr(208, "monto_indemnizacion", "NUMERIC(14,2)", 6)
add_attr(208, "deducible_aplicado", "NUMERIC(10,2)", 7)
add_attr(208, "monto_neto_desembolso", "NUMERIC(14,2)", 8)
add_attr(208, "estado_saga", "VARCHAR(40) [SAGA_COMPLETADA]", 9)
add_attr(208, "comprobante_transferencia", "VARCHAR(100)", 10)

# 9. dataset_historico_ml_polizas
add_table(209, 8, "dataset_historico_ml_polizas", "table", "1,200 Registros para ML Random Forest (CU12)")
add_attr(209, "id", "SERIAL [PK]", 1)
add_attr(209, "mes_registro", "DATE", 2)
add_attr(209, "edad_asegurado", "INT", 3)
add_attr(209, "antiguedad_licencia_anios", "INT", 4)
add_attr(209, "tipo_vehiculo", "VARCHAR(30)", 5)
add_attr(209, "valor_comercial_usd", "NUMERIC(10,2)", 6)
add_attr(209, "historial_siniestros_previos", "INT", 7)
add_attr(209, "perfil_riesgo_score", "NUMERIC(5,2)", 8)
add_attr(209, "prima_anual_calculada", "NUMERIC(10,2)", 9)
add_attr(209, "tuvo_siniestro_en_anio", "INT [0, 1]", 10)
add_attr(209, "costo_siniestro_usd", "NUMERIC(12,2)", 11)
add_attr(209, "polizas_vendidas_en_mes", "INT", 12)

# Layout PostgreSQL Diagram 31 (Grid amplio y limpio)
pg_layout = [
    # Fila 1: Usuarios, Clientes, Catálogo Planes y Coberturas
    (201, 50, 50, 360, 260),     # usuario
    (202, 430, 50, 760, 290),    # cliente
    (203, 830, 50, 1160, 240),   # plan_seguro
    (204, 1230, 50, 1560, 240),  # cobertura
    
    # Fila 2: Facturas, Póliza (Centro) y Pagos QR
    (206, 50, 370, 370, 620),    # factura_nota_venta
    (205, 430, 370, 780, 640),   # poliza
    (207, 850, 370, 1180, 610),  # pago_prima
    
    # Fila 3: Liquidaciones Saga y Dataset ML
    (208, 430, 720, 790, 970),   # orden_liquidacion_saga
    (209, 850, 720, 1210, 980)   # dataset_historico_ml_polizas
]
for cid, l, t, r, b in pg_layout:
    add_dobj(31, cid, l, t, r, b)

# Relaciones Relacionales PostgreSQL (FKs)
add_rel("FK_cliente_usuario", "Association", 202, 201, 31, "0..*", "1")
add_rel("FK_poliza_cliente", "Association", 205, 202, 31, "0..*", "1")
add_rel("FK_poliza_plan", "Association", 205, 203, 31, "0..*", "1")
add_rel("FK_cobertura_plan", "Association", 204, 203, 31, "1..*", "1")
add_rel("FK_factura_poliza", "Association", 206, 205, 31, "0..*", "1")
add_rel("FK_pago_poliza", "Association", 207, 205, 31, "0..*", "1")
add_rel("FK_saga_poliza", "Association", 208, 205, 31, "0..*", "1")
add_rel("FK_saga_cliente", "Association", 208, 202, 31, "0..*", "1")


# =============================================================================
# MODELO 2: MONGODB 7.0 (aegiscore_siniestros) - Colecciones Documentales y Subdocumentos BSON
# =============================================================================
# 1. expedientes_siniestros (Colección Core)
add_table(220, 9, "expedientes_siniestros", "collection", "Colección Documental BSON semiestructurada (MS2 NestJS Clean/CQRS)")
add_attr(220, "_id", "ObjectId [PK]", 1)
add_attr(220, "numero_reclamo", "String [UNIQUE INDEX]", 2)
add_attr(220, "poliza_id", "String [Ref PG polizas]", 3)
add_attr(220, "numero_poliza", "String", 4)
add_attr(220, "estado", "Enum [REPORTADO, EN_REVISION_IA, PERITAJE_COMPLETADO, LIQUIDADO]", 5)
add_attr(220, "tipo_siniestro", "Enum [CHOQUE_VIAL, ROBO_PARCIAL, ROBO_TOTAL, VUELCO]", 6)
add_attr(220, "geolocalizacion", "GeoJSON_Point [Índice 2dsphere]", 7)
add_attr(220, "triaje_ia", "Subdocument [Severidad y Piezas]", 8)
add_attr(220, "peritaje_campo", "Subdocument [Inspección Móvil TFLite]", 9)
add_attr(220, "idempotency_key", "String [UUIDv4 DynamoDB]", 10)
add_attr(220, "monto_estimado_reparacion", "Double", 11)
add_attr(220, "monto_indemnizacion_aprobado", "Double", 12)
add_attr(220, "created_at", "Date", 13)

# 2. GeoJSON_Point (Subdocumento Embebido con Índice 2dsphere)
add_table(221, 9, "GeoJSON_Point", "subdocument", "Estructura Geoespacial para Índice 2dsphere (Proximidad GPS)")
add_attr(221, "type", "String = 'Point'", 1)
add_attr(221, "coordinates", "Array<Double> [longitud, latitud]", 2)
add_attr(221, "«index»", "2dsphere (Radio de búsqueda en metros)", 3)

# 3. triaje_ia (Subdocumento Embebido)
add_table(222, 9, "triaje_ia_subdoc", "subdocument", "Resultado Inferencia Inmediata WhatsApp (CU06)")
add_attr(222, "gravedad", "String [BAJA, MEDIA, ALTA, PERDIDA_TOTAL]", 1)
add_attr(222, "score_danos", "Double [0.00 - 1.00]", 2)
add_attr(222, "piezas_detectadas", "Array<String> [PARACHOQUES, OPTICA, CAPO]", 3)
add_attr(222, "modelo_inferencia", "String [CrashNet-YOLO-v2.1]", 4)

# 4. peritaje_campo (Subdocumento Embebido)
add_table(223, 9, "peritaje_campo_subdoc", "subdocument", "Inspección Offline App Flutter SQLite + TFLite (CU07)")
add_attr(223, "perito_id", "String [UUID]", 1)
add_attr(223, "perito_nombre", "String", 2)
add_attr(223, "fecha_inspeccion", "Date", 3)
add_attr(223, "ocr_placa_detectada", "String", 4)
add_attr(223, "coincide_con_poliza", "Boolean", 5)
add_attr(223, "agente_tflite_valido", "Boolean", 6)
add_attr(223, "notas", "String", 7)

# 5. peritajes_ia_vision (Colección)
add_table(224, 9, "peritajes_ia_vision", "collection", "Mapas Grad-CAM y Pesos de Red Neuronal (CU11)")
add_attr(224, "_id", "ObjectId [PK]", 1)
add_attr(224, "expediente_id", "String [Ref expedientes_siniestros]", 2)
add_attr(224, "clase_dano_detectada", "String", 3)
add_attr(224, "confianza_score", "Double [ej. 0.942]", 4)
add_attr(224, "mapa_calor_gradcam_url", "String", 5)
add_attr(224, "fecha_analisis", "Date", 6)

# 6. alertas_fraude_anomalias (Colección)
add_table(225, 9, "alertas_fraude_anomalias", "collection", "Detección de Fraude Isolation Forest (CU13)")
add_attr(225, "_id", "ObjectId [PK]", 1)
add_attr(225, "reclamo_id", "String [Ref expedientes_siniestros]", 2)
add_attr(225, "score_anomalia", "Double [-1.00 a +1.00]", 3)
add_attr(225, "motivo_sospecha", "String", 4)
add_attr(225, "fecha_alerta", "Date", 5)

# 7. bitacora_agente_autonomo (Colección)
add_table(226, 9, "bitacora_agente_autonomo", "collection", "Traza de Razonamiento del Agente LangGraph (CU14)")
add_attr(226, "_id", "ObjectId [PK]", 1)
add_attr(226, "meta_ejecutada", "String [SUPERVISION_SINIESTROS, REASIGNACION]", 2)
add_attr(226, "pensamiento_cadena", "String [Chain-of-Thought]", 3)
add_attr(226, "tool_mcp_invocada", "String [consultar_clima, asignar_perito]", 4)
add_attr(226, "resultado_ejecucion", "Object [JSON Payload]", 5)
add_attr(226, "timestamp", "Date", 6)

# Layout MongoDB Diagram 32 (Expediente al centro y subdocumentos/colecciones alrededor)
mongo_layout = [
    (221, 50, 50, 370, 170),      # GeoJSON_Point
    (222, 50, 220, 370, 360),     # triaje_ia_subdoc
    (220, 440, 50, 850, 360),     # expedientes_siniestros (Centro Arriba)
    (223, 920, 50, 1270, 250),    # peritaje_campo_subdoc
    (224, 50, 440, 390, 610),     # peritajes_ia_vision
    (225, 470, 440, 820, 600),    # alertas_fraude_anomalias
    (226, 900, 440, 1300, 610)    # bitacora_agente_autonomo
]
for cid, l, t, r, b in mongo_layout:
    add_dobj(32, cid, l, t, r, b)

# Relaciones Documentales MongoDB (Embebidos y Referencias)
add_rel("embeds (2dsphere)", "Aggregation", 220, 221, 32, "1", "1")
add_rel("embeds (Triaje)", "Aggregation", 220, 222, 32, "1", "1")
add_rel("embeds (Inspección)", "Aggregation", 220, 223, 32, "1", "1")
add_rel("ref_expediente", "Association", 224, 220, 32, "0..*", "1")
add_rel("ref_reclamo", "Association", 225, 220, 32, "0..*", "1")


# =============================================================================
# MODELO 3: AMAZON DYNAMODB (AWS / Local) - Tablas NoSQL Clave-Valor e Idempotencia
# =============================================================================
# 1. IdempotencyRecords (Control de Duplicados de Alta Velocidad < 5ms)
add_table(230, 10, "IdempotencyRecords", "table", "Tabla NoSQL Clave-Valor de Alta Velocidad con TTL (<5ms) - CU08 y CU10")
add_attr(230, "idempotency_key", "String [HASH / Partition Key - UUIDv4]", 1)
add_attr(230, "request_hash", "String [SHA-256 del Body JSON]", 2)
add_attr(230, "status", "String [IN_PROGRESS | COMPLETED | FAILED]", 3)
add_attr(230, "response_payload", "String [JSON Serializado de Respuesta]", 4)
add_attr(230, "http_status_code", "Number [ej. 200, 201, 400]", 5)
add_attr(230, "ttl", "Number [TTL Expiration Epoch Timestamp]", 6)
add_attr(230, "created_at", "String [ISO 8601 UTC]", 7)

# 2. SesionesSSO (Caché Distribuido de Tokens Keycloak)
add_table(231, 10, "SesionesSSO", "table", "Sesiones Rápidas y Revocación de Tokens OIDC Keycloak (CU01)")
add_attr(231, "session_id", "String [HASH / Partition Key]", 1)
add_attr(231, "user_id", "String [UUID del Usuario]", 2)
add_attr(231, "access_token_jti", "String [JWT Token Identifier]", 3)
add_attr(231, "roles", "StringSet [ADMIN, PERITO, ACTUARIO]", 4)
add_attr(231, "expires_at", "Number [TTL Epoch Timestamp]", 5)
add_attr(231, "last_activity", "String [ISO 8601 UTC]", 6)

# Layout DynamoDB Diagram 33 (2 Tablas Grandes Bien Separadas)
dynamo_layout = [
    (230, 80, 80, 520, 310),     # IdempotencyRecords
    (231, 720, 80, 1140, 290)    # SesionesSSO con espacio amplio en el medio
]
for cid, l, t, r, b in dynamo_layout:
    add_dobj(33, cid, l, t, r, b)

# Dependencia conceptual entre ambas
add_rel("Validación OIDC & Mutaciones", "Dependency", 230, 231, 33)

conn.commit()
conn.close()
print("Modelos de Base de Datos PostgreSQL, MongoDB y DynamoDB regenerados con éxito con coordenadas negativas.")
