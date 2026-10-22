#!/usr/bin/env python3
"""
=============================================================================
 AegisCore AI - Script de Verificación de Salud de Bases de Datos Cloud
 Conectividad real a:
   1. Neon Serverless PostgreSQL (Relacional ACID)
   2. MongoDB Atlas Cloud (Documental NoSQL)
   3. Amazon DynamoDB Cloud us-east-2 (Idempotencia Transversal)
=============================================================================
"""

import os
import sys

# Asegurar codificación utf-8 en consolas Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Color formatting helpers for console output
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Cargar variables de entorno desde .env si existe en la raíz
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file_path = os.path.join(ROOT_DIR, ".env")
if os.path.isfile(env_file_path):
    with open(env_file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k not in os.environ:
                    os.environ[k] = v

NEON_URL = os.getenv("DATABASE_URL")
MONGO_URI = os.getenv("MONGODB_URI")
AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")
DYNAMO_TABLE = os.getenv("DYNAMODB_TABLE_IDEMPOTENCY", "AegisCore_IdempotencyRecords")


def test_neon() -> bool:
    print(f"{CYAN}[1/3] Probando conexión a Neon Serverless PostgreSQL...{RESET}")
    try:
        import psycopg2
        # Clean URL if it has unsupported driver extensions
        clean_url = NEON_URL.replace("&channel_binding=require", "")
        conn = psycopg2.connect(clean_url, connect_timeout=10)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        cur.execute("SELECT current_database(), current_user;")
        db_name, db_user = cur.fetchone()
        cur.close()
        conn.close()
        print(f"  {GREEN}✔ Conexión EXITOSA a Neon PostgreSQL{RESET}")
        print(f"    • Base de Datos: {BOLD}{db_name}{RESET}")
        print(f"    • Usuario: {BOLD}{db_user}{RESET}")
        print(f"    • Motor: {version.split(',')[0]}")
        return True
    except Exception as e:
        print(f"  {RED}✘ Falló conexión a Neon PostgreSQL:{RESET} {e}")
        return False


def test_mongo() -> bool:
    print(f"\n{CYAN}[2/3] Probando conexión a MongoDB Atlas Cloud...{RESET}")
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
        ping_res = client.admin.command("ping")
        db = client.get_database("aegiscore_siniestros_db")
        collections = db.list_collection_names()
        client.close()
        print(f"  {GREEN}✔ Conexión EXITOSA a MongoDB Atlas{RESET}")
        print(f"    • Ping Response: {BOLD}{ping_res}{RESET}")
        print(f"    • Base de Datos: {BOLD}aegiscore_siniestros_db{RESET}")
        print(f"    • Colecciones existentes: {collections if collections else '(vacía, lista para poblar)'}")
        return True
    except Exception as e:
        print(f"  {RED}✘ Falló conexión a MongoDB Atlas:{RESET} {e}")
        return False


def test_dynamo() -> bool:
    print(f"\n{CYAN}[3/3] Probando conexión a Amazon DynamoDB Cloud ({AWS_REGION})...{RESET}")
    try:
        import boto3
        client = boto3.client(
            "dynamodb",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_KEY,
            aws_secret_access_key=AWS_SECRET
        )
        # Describe target idempotency table
        res = client.describe_table(TableName=DYNAMO_TABLE)
        table_desc = res["Table"]
        table_status = table_desc["TableStatus"]
        item_count = table_desc.get("ItemCount", 0)

        # Check TTL status
        ttl_res = client.describe_time_to_live(TableName=DYNAMO_TABLE)
        ttl_status = ttl_res["TimeToLiveDescription"]["TimeToLiveStatus"]
        ttl_attr = ttl_res["TimeToLiveDescription"].get("AttributeName", "N/A")

        print(f"  {GREEN}✔ Conexión EXITOSA a Amazon DynamoDB Cloud{RESET}")
        print(f"    • Tabla: {BOLD}{DYNAMO_TABLE}{RESET}")
        print(f"    • Estado de Tabla: {BOLD}{table_status}{RESET}")
        print(f"    • TTL Estado: {BOLD}{ttl_status}{RESET} (Atributo: {ttl_attr})")
        print(f"    • Items aproximados: {item_count}")
        return True
    except Exception as e:
        print(f"  {RED}✘ Falló conexión a DynamoDB Cloud:{RESET} {e}")
        return False


def main():
    print(f"{BOLD}============================================================================={RESET}")
    print(f"{BOLD}   AEGISCORE AI :: VERIFICACIÓN DE PERSISTENCIA POLÍGLOTA CLOUD              {RESET}")
    print(f"{BOLD}============================================================================={RESET}")

    neon_ok = test_neon()
    mongo_ok = test_mongo()
    dynamo_ok = test_dynamo()

    print(f"\n{BOLD}============================================================================={RESET}")
    if neon_ok and mongo_ok and dynamo_ok:
        print(f"{GREEN}{BOLD}  🎉 ¡TODAS LAS BASES DE DATOS CLOUD ESTÁN 100% OPERATIVAS Y CONECTADAS!{RESET}")
        print(f"{GREEN}  1. Neon PostgreSQL      -> OK (ACID Relacional){RESET}")
        print(f"{GREEN}  2. MongoDB Atlas        -> OK (Documental Siniestros){RESET}")
        print(f"{GREEN}  3. Amazon DynamoDB      -> OK (Idempotencia Sub-milisegundo){RESET}")
        print(f"{BOLD}============================================================================={RESET}")
        sys.exit(0)
    else:
        print(f"{RED}{BOLD}  ⚠️ AL MENOS UNA BASE DE DATOS PRESENTÓ ERRORES DE CONECTIVIDAD.{RESET}")
        print(f"{BOLD}============================================================================={RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
