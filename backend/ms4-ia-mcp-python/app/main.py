"""
=============================================================================
 AegisCore AI - MS4: Inteligencia Artificial, Deep Learning, Agentes y Servidor MCP
 Microservicio Python 3.11 / FastAPI
 Responsable de CU11, CU12, CU13, CU14 y CU15
=============================================================================
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import datetime
import os
import re

app = FastAPI(
    title="AegisCore AI - Machine Learning, Deep Learning & MCP Server",
    description="Microservicio de IA que gestiona Random Forest (CU12), K-Means & Isolation Forest (CU13), TensorFlow (CU11), Agentes LangGraph (CU14) y Servidor MCP con blindaje Anti-SQLi (CU15).",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.db.connections import (
    get_mongo_client,
    get_mongo_db,
    get_idempotency_table,
    get_postgres_connection,
)

# ---------------------------------------------------------------------------
# Health Check General y de Bases de Datos Cloud
# ---------------------------------------------------------------------------
@app.get("/health")
def health_check():
    return {
        "status": "UP",
        "service": "ms4-ia-mcp-python",
        "framework": "FastAPI",
        "python_version": "3.11",
        "cloud_persistence": {
            "relational": "Neon Serverless PostgreSQL (CU12, CU15)",
            "document": "MongoDB Atlas Cloud (CU06, CU11, CU14)",
            "key_value": "Amazon DynamoDB Cloud us-east-2 (CU08, CU10)"
        },
        "components": {
            "ml_supervised": "Scikit-Learn Random Forest (CU12)",
            "ml_unsupervised": "K-Means & Isolation Forest (CU13)",
            "dl_vision": "TensorFlow / Keras CNN CrashNet (CU11)",
            "agents": "LangGraph Goals & Skills Autonomous Agent (CU14)",
            "mcp_voice_reports": "Model Context Protocol + Whisper STT + OWASP Anti-SQLi (CU15)"
        },
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.get("/health/cloud-dbs")
def health_cloud_dbs():
    results = {}
    
    # 1. Neon PostgreSQL
    try:
        conn = get_postgres_connection()
        cur = conn.cursor()
        cur.execute("SELECT current_database(), current_user;")
        db_name, db_user = cur.fetchone()
        cur.close()
        conn.close()
        results["neon_postgresql"] = {"status": "CONNECTED", "database": db_name, "user": db_user}
    except Exception as e:
        results["neon_postgresql"] = {"status": "ERROR", "detail": str(e)}

    # 2. MongoDB Atlas
    try:
        client = get_mongo_client()
        ping = client.admin.command("ping")
        results["mongodb_atlas"] = {"status": "CONNECTED", "ping": ping}
    except Exception as e:
        results["mongodb_atlas"] = {"status": "ERROR", "detail": str(e)}

    # 3. Amazon DynamoDB Cloud
    try:
        table = get_idempotency_table()
        table_status = table.table_status
        results["dynamodb_cloud"] = {"status": "CONNECTED", "table": table.name, "table_status": table_status}
    except Exception as e:
        results["dynamodb_cloud"] = {"status": "ERROR", "detail": str(e)}

    all_ok = all(v.get("status") == "CONNECTED" for v in results.values())
    return {
        "status": "ALL_HEALTHY" if all_ok else "DEGRADED",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "databases": results
    }

# ---------------------------------------------------------------------------
# CU12: Machine Learning Supervisado (Random Forest) - Router Modular ICONIX
# ---------------------------------------------------------------------------
from app.boundaries.ml_supervised_router import router as ml_supervised_router
app.include_router(ml_supervised_router)

# ---------------------------------------------------------------------------
# CU13: Machine Learning No Supervisado (K-Means + Isolation Forest) - Router Modular ICONIX
# ---------------------------------------------------------------------------
from app.boundaries.ml_unsupervised_router import router as ml_unsupervised_router
from app.controls.unsupervised_fraud_control import unsupervised_control
app.include_router(ml_unsupervised_router)

@app.get("/api/ml/clusters-and-anomalies", tags=["CU13 - Machine Learning No Supervisado (K-Means & Isolation Forest)"])
def get_clusters_and_anomalies_legacy():
    """Endpoint de compatibilidad directa que redirige al Control ICONIX."""
    return unsupervised_control.obtener_resumen_dashboard()

# ---------------------------------------------------------------------------
# CU11: Deep Learning TensorFlow / Keras (Imagen y Video de Choques) - Router Modular ICONIX
# ---------------------------------------------------------------------------
from app.boundaries.dl_vision_router import router as dl_vision_router
app.include_router(dl_vision_router)

# ---------------------------------------------------------------------------
# CU14: Agente Autónomo LangGraph (Metas, Re-planning y Skills) - Router Modular ICONIX
# ---------------------------------------------------------------------------
from app.boundaries.agent_monitor_router import router as agent_monitor_router
from app.controls.langgraph_autonomous_agent import langgraph_agent_control
app.include_router(agent_monitor_router)

@app.post("/api/agent/trigger-evaluation", tags=["CU14 - Agente Autónomo LangGraph (Metas, Re-planning & Skills)"])
def trigger_agent_evaluation_legacy():
    """Endpoint legado de compatibilidad que dispara el ciclo del Grafo LangGraph."""
    res = langgraph_agent_control.ejecutar_ciclo_autonomo()
    return {
        "agente": "AutonomousInsuranceAgent",
        "framework": "LangGraph",
        "ciclo_id": res.ciclo_id,
        "reflexion": res.reflexion_final,
        "skills_disparadas": res.skills_disparadas,
        "siniestros_resueltos": res.siniestros_resueltos
    }

# ---------------------------------------------------------------------------
# CU15: Servidor MCP, Whisper STT, Blindaje OWASP Anti-SQLi y Exportación (ICONIX)
# ---------------------------------------------------------------------------
from app.boundaries.voice_mcp_router import router as voice_mcp_router
from app.controls.voice_mcp_control import VoiceMcpControl
app.include_router(voice_mcp_router)

legacy_voice_control = VoiceMcpControl()

class LegacyVoiceReportRequest(BaseModel):
    comando_voz_transcrito: str
    formato_exportacion: Optional[str] = "XLSX"

@app.post("/api/mcp/voice-report", tags=["CU15 - Voice MCP Reports & Anti-SQLi"])
def process_voice_report_legacy(payload: LegacyVoiceReportRequest):
    """Endpoint de compatibilidad directa que redirige al Control ICONIX de CU15."""
    res = legacy_voice_control.procesarComandoVozCompleto(
        audio_bytes=None,
        texto_dictado=payload.comando_voz_transcrito,
        formato_preferido=payload.formato_exportacion.lower()
    )
    if res.auditoria_seguridad.es_amenaza:
        raise HTTPException(
            status_code=400,
            detail=f"[ALERTA OWASP DE SEGURIDAD] Intento de inyección SQL neutralizado [{res.auditoria_seguridad.rule_triggered}]. Petición bloqueada."
        )
    return {
        "protocolo": "Model Context Protocol (MCP) Server v1.0",
        "whisper_stt_transcripcion": res.transcripcion,
        "filtro_owasp_status": "SEGURO - Inyección SQL Bloqueada al 100%",
        "mcp_tool_ejecutada": res.intencion_detectada,
        "traza_mcp": res.traza_mcp.model_dump() if res.traza_mcp else {},
        "kpis_resumen": res.kpis_resumen,
        "descarga_generada": {
            "nombre_archivo": res.documento.filename if res.documento else "",
            "url_descarga": res.documento.download_url if res.documento else "",
            "sha256": res.documento.sha256_hash if res.documento else "",
            "tamano_kb": res.documento.file_size_kb if res.documento else 0.0,
            "formato": res.formato_solicitado.upper()
        }
    }

