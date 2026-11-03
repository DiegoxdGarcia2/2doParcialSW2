"""
=============================================================================
 AegisCore AI - MS4: Configuración Centralizada (Pydantic Settings)
=============================================================================
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import load_dotenv, find_dotenv

# Cargar automáticamente .env buscando hacia arriba en el árbol de directorios
_dotenv_path = find_dotenv(usecwd=True)
if not _dotenv_path:
    _curr = Path(__file__).resolve()
    for _ in range(5):
        _curr = _curr.parent
        _candidate = _curr / ".env"
        if _candidate.is_file():
            _dotenv_path = str(_candidate)
            break
if _dotenv_path:
    load_dotenv(_dotenv_path)


class Settings(BaseSettings):
    PROJECT_NAME: str = "AegisCore AI - MS4 IA, MCP & Machine Learning"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"

    # Bases de Datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    MONGO_INITDB_DATABASE: str = os.getenv("MONGO_INITDB_DATABASE", "aegiscore_siniestros_db")
    # Amazon DynamoDB
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-2")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    DYNAMODB_TABLE_IDEMPOTENCY: str = os.getenv("DYNAMODB_TABLE_IDEMPOTENCY", "AegisCore_IdempotencyRecords")

    # Amazon S3 (Multimedia, Evidencias Jerárquicas y Reportes Duales)
    S3_BUCKET_NAME: str = os.getenv("AWS_S3_BUCKET") or os.getenv("S3_BUCKET_NAME") or "servicio-de-seguros-aegiscore"
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET") or os.getenv("S3_BUCKET_NAME") or "servicio-de-seguros-aegiscore"
    AWS_S3_REGION: str = os.getenv("AWS_S3_REGION") or os.getenv("AWS_REGION") or "us-east-2"
    AWS_S3_ACCESS_KEY_ID: str = os.getenv("AWS_S3_ACCESS_KEY_ID") or os.getenv("AWS_ACCESS_KEY_ID") or ""
    AWS_S3_SECRET_ACCESS_KEY: str = os.getenv("AWS_S3_SECRET_ACCESS_KEY") or os.getenv("AWS_SECRET_ACCESS_KEY") or ""
    AWS_S3_PUBLIC_URL: str = os.getenv("AWS_S3_PUBLIC_URL") or "https://servicio-de-seguros-aegiscore.s3.us-east-2.amazonaws.com"
    S3_PRESIGNED_EXPIRATION_SECONDS: int = int(os.getenv("S3_PRESIGNED_EXPIRATION_SECONDS", "900"))

    # Keycloak SSO
    KEYCLOAK_URL: str = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
    KEYCLOAK_REALM: str = os.getenv("KEYCLOAK_REALM", "aegiscore")
    KEYCLOAK_CLIENT_ID: str = os.getenv("KEYCLOAK_CLIENT_ID", "aegiscore-api-gateway")

    # Rutas de artefactos de Machine Learning
    ML_ARTIFACTS_DIR: Path = Path(__file__).resolve().parent.parent / "ml_artifacts"

    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")


settings = Settings()
settings.ML_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
