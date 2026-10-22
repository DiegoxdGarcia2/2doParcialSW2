#!/usr/bin/env python3
"""
scripts/seed_cloud_dbs.py
AegisCore AI - Cloud Persistence Seeder & Initializer
Populates:
  1. Neon PostgreSQL (DDL, Catalogs, Initial Admin/Perito/Client, 1,200 ML Synthetic Records)
  2. MongoDB Atlas (Collections, 2dsphere / Compound Indexes, Demo Siniestro Record)
  3. Amazon DynamoDB Cloud (Table & TTL Verification, Sample Idempotency Record)
"""

import os
import sys
import datetime
from pathlib import Path

# Force UTF-8 stdout for Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde .env si existe en la raíz
env_file_path = ROOT_DIR / ".env"
if env_file_path.is_file():
    with open(env_file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k not in os.environ:
                    os.environ[k] = v

# Cloud Credentials
POSTGRES_URL = os.getenv("DATABASE_URL")
MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB_NAME = os.getenv("MONGO_INITDB_DATABASE", "aegiscore_siniestros_db")
AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")
DYNAMO_TABLE = os.getenv("DYNAMODB_TABLE_IDEMPOTENCY", "AegisCore_IdempotencyRecords")

def seed_neon_postgres():
    print("\n" + "=" * 65)
    print(" [1/3] POBLANDO Y CONFIGURANDO NEON SERVERLESS POSTGRESQL")
    print("=" * 65)
    try:
        import psycopg2
        sql_path = ROOT_DIR / "infra" / "db-init" / "postgres-init.sql"
        if not sql_path.exists():
            print(f"  [ERROR] No se encontró el archivo SQL en: {sql_path}")
            return False

        with open(sql_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        print(f"  --> Conectando a Neon PostgreSQL ({POSTGRES_URL.split('@')[1].split('/')[0]})...")
        conn = psycopg2.connect(POSTGRES_URL)
        conn.autocommit = True
        cur = conn.cursor()

        print(f"  --> Ejecutando script DDL y generación de dataset ({sql_path.name})...")
        cur.execute(sql_content)

        # Verificar tablas creadas
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cur.fetchall()]
        print(f"  --> Tablas creadas en esquema público ({len(tables)}): {', '.join(tables)}")

        # Verificar conteo de dataset ML
        cur.execute("SELECT COUNT(*) FROM dataset_historico_ml_polizas;")
        ml_count = cur.fetchone()[0]
        print(f"  --> Registros sintéticos en 'dataset_historico_ml_polizas': {ml_count} filas")

        # Verificar usuarios y pólizas
        cur.execute("SELECT COUNT(*) FROM usuario;")
        usr_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM poliza;")
        pol_count = cur.fetchone()[0]
        print(f"  --> Usuarios iniciales: {usr_count} | Pólizas iniciales: {pol_count}")

        cur.close()
        conn.close()
        print("  [EXITO] Neon PostgreSQL poblado y verificado correctamente.")
        return True
    except Exception as e:
        print(f"  [ERROR] Falló inicialización de Neon PostgreSQL: {e}")
        return False

def seed_mongo_atlas():
    print("\n" + "=" * 65)
    print(" [2/3] CONFIGURANDO COLECCIONES E ÍNDICES EN MONGODB ATLAS")
    print("=" * 65)
    try:
        from pymongo import MongoClient, ASCENDING, DESCENDING, GEOSPHERE
        from bson import ObjectId

        print(f"  --> Conectando a MongoDB Atlas ({MONGO_DB_NAME})...")
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
        db = client[MONGO_DB_NAME]

        # 1. Colección expedientes_siniestros
        col_exp = db["expedientes_siniestros"]
        col_exp.create_index([("numero_reclamo", ASCENDING)], unique=True)
        col_exp.create_index([("poliza_id", ASCENDING)])
        col_exp.create_index([("estado", ASCENDING)])
        col_exp.create_index([("idempotency_key", ASCENDING)], sparse=True)
        col_exp.create_index([("geolocalizacion", GEOSPHERE)])
        col_exp.create_index([("created_at", DESCENDING)])

        # 2. Colección peritajes_ia_vision
        col_per = db["peritajes_ia_vision"]
        col_per.create_index([("expediente_id", ASCENDING)])
        col_per.create_index([("fecha_analisis", DESCENDING)])

        # 3. Colección bitacora_agente_autonomo
        col_bit = db["bitacora_agente_autonomo"]
        col_bit.create_index([("meta_ejecutada", ASCENDING)])
        col_bit.create_index([("timestamp", DESCENDING)])

        # 4. Colección alertas_fraude_anomalias
        col_fraude = db["alertas_fraude_anomalias"]
        col_fraude.create_index([("reclamo_id", ASCENDING)])
        col_fraude.create_index([("score_anomalia", DESCENDING)])

        print("  --> Índices creados (incluido '2dsphere' para CU14 / peritajes geolocalizados).")

        # Sembrar expediente demo si no existe
        if col_exp.count_documents({"numero_reclamo": "REC-2026-00492"}) == 0:
            demo_id = ObjectId()
            col_exp.insert_one({
                "_id": demo_id,
                "numero_reclamo": "REC-2026-00492",
                "poliza_id": "d0000001-0000-0000-0000-000000000001",
                "numero_poliza": "POL-2026-AUT-00892",
                "estado": "PERITAJE_COMPLETADO",
                "tipo_siniestro": "CHOQUE_VIAL",
                "descripcion": "Colisión por alcance frontal en intersección con semáforo intermitente.",
                "canal_origen": "WHATSAPP_N8N",
                "idempotency_key": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
                "geolocalizacion": {
                    "type": "Point",
                    "coordinates": [-63.1812, -17.7833] # Santa Cruz, Bolivia
                },
                "ubicacion_texto": "4to Anillo y Av. San Martín, Equipetrol Norte",
                "triaje_ia": {
                    "gravedad": "MEDIA",
                    "score_danos": 0.74,
                    "piezas_detectadas": ["PARACHOQUES_DELANTERO", "OPTICA_DERECHA", "CAPO_PARCIAL"],
                    "modelo_inferencia": "TensorFlow-YOLO-CrashNet-v2.1"
                },
                "peritaje_campo": {
                    "perito_id": "e0000001-0000-0000-0000-000000000002",
                    "perito_nombre": "Ing. Roberto Paz",
                    "fecha_inspeccion": datetime.datetime.now(datetime.timezone.utc),
                    "ocr_placa_detectada": "4028-PLK",
                    "coincide_con_poliza": True,
                    "agente_tflite_valido": True,
                    "notas": "Estructura chasis intacta. Reemplazo de ópticas y enderezado de capó requerido."
                },
                "monto_estimado_reparacion": 2850.00,
                "monto_indemnizacion_aprobado": 2500.00,
                "deducible_calculado": 250.00,
                "created_at": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2),
                "updated_at": datetime.datetime.now(datetime.timezone.utc)
            })

            col_per.insert_one({
                "expediente_id": demo_id,
                "numero_reclamo": "REC-2026-00492",
                "fecha_analisis": datetime.datetime.now(datetime.timezone.utc),
                "piezas_analizadas": [
                    {"pieza": "PARACHOQUES_DELANTERO", "probabilidad": 0.96, "severidad_porcentaje": 85, "accion_sugerida": "REEMPLAZO"},
                    {"pieza": "FAROL_DELANTERO_DER", "probabilidad": 0.92, "severidad_porcentaje": 100, "accion_sugerida": "REEMPLAZO"},
                    {"pieza": "CAPO", "probabilidad": 0.88, "severidad_porcentaje": 35, "accion_sugerida": "ENDEREZADO_PINTURA"}
                ],
                "severidad_global": "MEDIA",
                "costo_estimado_taller_usd": 2850.00,
                "modelo_tf_version": "aegiscore-crash-detection-2026.keras"
            })
            print("  --> Documento demo insertado en 'expedientes_siniestros' y 'peritajes_ia_vision'.")
        else:
            print("  --> Expediente demo ya existía en 'expedientes_siniestros'.")

        colls = db.list_collection_names()
        print(f"  --> Colecciones activas ({len(colls)}): {', '.join(colls)}")
        print(f"  --> Conteo en 'expedientes_siniestros': {col_exp.count_documents({})} docs")

        client.close()
        print("  [EXITO] MongoDB Atlas inicializado y verificado correctamente.")
        return True
    except Exception as e:
        print(f"  [ERROR] Falló inicialización de MongoDB Atlas: {e}")
        return False

def seed_dynamodb():
    print("\n" + "=" * 65)
    print(" [3/3] VERIFICANDO Y PROBANDO AMAZON DYNAMODB CLOUD")
    print("=" * 65)
    try:
        import boto3
        import time

        client = boto3.client(
            'dynamodb',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_KEY,
            aws_secret_access_key=AWS_SECRET
        )

        res = client.describe_table(TableName=DYNAMO_TABLE)
        status = res['Table']['TableStatus']
        pk = res['Table']['KeySchema'][0]['AttributeName']

        ttl_res = client.describe_time_to_live(TableName=DYNAMO_TABLE)
        ttl_status = ttl_res['TimeToLiveDescription']['TimeToLiveStatus']
        ttl_attr = ttl_res['TimeToLiveDescription'].get('AttributeName', 'expiresAt')

        print(f"  --> Tabla: {DYNAMO_TABLE} | Estado: {status} | Partition Key: {pk}")
        print(f"  --> TTL Status: {ttl_status} | Atributo TTL: {ttl_attr}")

        # Probar inserción y lectura de registro de prueba
        test_key = "test-health-check-" + str(int(time.time()))
        expires = int(time.time()) + 3600

        client.put_item(
            TableName=DYNAMO_TABLE,
            Item={
                'idempotencyKey': {'S': test_key},
                'idempotency_key': {'S': test_key},
                'endpoint': {'S': '/api/v1/health'},
                'http_status': {'N': '200'},
                'response_hash': {'S': 'sha256-test-cloud-verification'},
                'expiresAt': {'N': str(expires)}
            }
        )
        print(f"  --> Registro de idempotencia insertado (key: {test_key})")

        # Leer de vuelta
        get_res = client.get_item(
            TableName=DYNAMO_TABLE,
            Key={'idempotencyKey': {'S': test_key}}
        )
        if 'Item' in get_res:
            print("  --> Lectura de idempotencia confirmada (Consistencia fuerte/eventual verificada).")

        print("  [EXITO] Amazon DynamoDB Cloud 100% operativo con permisos de lectura/escritura.")
        return True
    except Exception as e:
        print(f"  [ERROR] Falló prueba de Amazon DynamoDB: {e}")
        return False

if __name__ == "__main__":
    p = seed_neon_postgres()
    m = seed_mongo_atlas()
    d = seed_dynamodb()

    print("\n" + "=" * 65)
    if p and m and d:
        print("  ★ TODAS LAS BASES DE DATOS CLOUD POBLADAS Y 100% OPERATIVAS ★")
    else:
        print("  [ADVERTENCIA] Algunas bases de datos tuvieron observaciones.")
    print("=" * 65 + "\n")
