"""
=============================================================================
 AegisCore AI - MS4: Conexiones de Persistencia Políglota Cloud
 Microservicio Python 3.11 / FastAPI
 Gestiona:
   1. MongoDB Atlas (Expedientes de Siniestros y Peritajes IA)
   2. Amazon DynamoDB Cloud (Idempotencia y Locks)
   3. Neon Serverless PostgreSQL (Réplica analítica para Random Forest y MCP)
=============================================================================
"""

import os
from functools import lru_cache
from typing import Optional
import boto3
from pathlib import Path
from pymongo import MongoClient
from pymongo.database import Database
import psycopg2

from dotenv import load_dotenv, find_dotenv
# Cargar automáticamente .env buscando hacia arriba en el árbol de directorios
_dotenv_path = find_dotenv(usecwd=True)
if not _dotenv_path:
    # Intento relativo al archivo actual
    _curr = Path(__file__).resolve()
    for _ in range(5):
        _curr = _curr.parent
        _candidate = _curr / ".env"
        if _candidate.is_file():
            _dotenv_path = str(_candidate)
            break
if _dotenv_path:
    load_dotenv(_dotenv_path)

# ---------------------------------------------------------------------------
# 1. MongoDB Atlas Client
# ---------------------------------------------------------------------------
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/aegiscore_siniestros_db")
MONGO_DB_NAME = os.getenv("MONGO_INITDB_DATABASE", "aegiscore_siniestros_db")

_mongo_client: Optional[MongoClient] = None


def get_mongo_client() -> MongoClient:
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=8000,
            maxPoolSize=50,
            minPoolSize=5
        )
    return _mongo_client


def get_mongo_db() -> Database:
    client = get_mongo_client()
    return client[MONGO_DB_NAME]


# ---------------------------------------------------------------------------
# 2. Amazon DynamoDB Cloud Resource & Client
# ---------------------------------------------------------------------------
AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")
DYNAMO_TABLE_NAME = os.getenv("DYNAMODB_TABLE_IDEMPOTENCY", "AegisCore_IdempotencyRecords")

_dynamo_resource = None


def get_dynamo_resource():
    global _dynamo_resource
    if _dynamo_resource is None:
        kwargs = {"region_name": AWS_REGION}
        if AWS_KEY and AWS_SECRET:
            kwargs["aws_access_key_id"] = AWS_KEY
            kwargs["aws_secret_access_key"] = AWS_SECRET
        _dynamo_resource = boto3.resource("dynamodb", **kwargs)
    return _dynamo_resource


def get_idempotency_table():
    resource = get_dynamo_resource()
    return resource.Table(DYNAMO_TABLE_NAME)


# ---------------------------------------------------------------------------
# 3. Neon Serverless PostgreSQL Connection
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")


def get_postgres_connection():
    db_url = os.getenv("DATABASE_URL") or DATABASE_URL
    if not db_url:
        raise ValueError("DATABASE_URL no está definida en las variables de entorno.")
    clean_url = db_url.replace("&channel_binding=require", "")
    return psycopg2.connect(clean_url, connect_timeout=10)
