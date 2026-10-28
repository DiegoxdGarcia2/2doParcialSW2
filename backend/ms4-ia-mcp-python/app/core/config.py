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
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-2")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    DYNAMODB_TABLE_IDEMPOTENCY: str = os.getenv("DYNAMODB_TABLE_IDEMPOTENCY", "AegisCore_IdempotencyRecords")

    # Keycloak SSO
    KEYCLOAK_URL: str = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
    KEYCLOAK_REALM: str = os.getenv("KEYCLOAK_REALM", "aegiscore")
    KEYCLOAK_CLIENT_ID: str = os.getenv("KEYCLOAK_CLIENT_ID", "aegiscore-api-gateway")

    # Rutas de artefactos de Machine Learning
    ML_ARTIFACTS_DIR: Path = Path(__file__).resolve().parent.parent / "ml_artifacts"

    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")


settings = Settings()
settings.ML_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
