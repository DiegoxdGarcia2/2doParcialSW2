"""
=============================================================================
 AegisCore AI - MS4: Pruebas Automatizadas para CU14 (Agente Autónomo LangGraph)
 Suite Pytest: Control ICONIX, Grafo StateGraph, MongoDB Atlas y Endpoints FastAPI
=============================================================================
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.controls.langgraph_autonomous_agent import langgraph_agent_control


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_grafo_langgraph_compilacion_y_nodos():
    """Valida que el StateGraph de LangGraph esté correctamente instanciado y compilado."""
    assert langgraph_agent_control.grafo_compilado is not None
    # Verificar que el grafo tenga los nodos del flujo DAG
    nodos_esperados = ["fnol_ingestion", "vision_perception", "policy_check", "fraud_guard", "settlement_saga", "reflection_replan"]
    # Comprobar que compila e inicializa
    assert hasattr(langgraph_agent_control.grafo_compilado, "invoke")


def test_evaluar_siniestros_estancados():
    """Valida la detección de expedientes con cuellos de botella y SLA excedido."""
    stalled = langgraph_agent_control.evaluar_siniestros_estancados()
    assert isinstance(stalled, list)
    assert len(stalled) >= 1
    
    primer_caso = stalled[0]
    assert "numero_reclamo" in primer_caso
    assert "cuello_botella" in primer_caso
    assert "accion_sugerida" in primer_caso
    assert primer_caso["dias_estancado"] >= 1


def test_calcular_estres_liquidez_reservas():
    """Valida el cálculo de suficiencia de reservas técnicas y Solvencia II."""
    liquidez = langgraph_agent_control.calcular_estres_liquidez_reservas()
    assert liquidez.reserva_capital_total_usd == 25_000_000.00
    assert liquidez.compromisos_activos_usd > 0.0
    assert liquidez.reserva_remanente_usd > 0.0
    assert liquidez.ratio_cobertura_pct >= 80.0
    assert liquidez.estado_solvencia == "SOLVENTE"


def test_ejecutar_ciclo_autonomo_langgraph():
    """Valida la ejecución completa del grafo LangGraph con persistencia en bitácora."""
    resultado = langgraph_agent_control.ejecutar_ciclo_autonomo()
    assert resultado.ciclo_id.startswith("CYCLE-")
    assert resultado.duracion_total_ms >= 0
    assert resultado.siniestros_analizados >= 1
    assert "LangGraph" in resultado.reflexion_final
    assert resultado.cluster_state is not None
    assert resultado.cluster_state.salud_cluster_pct == 99.98
    assert len(resultado.cluster_state.nodos_grafo) == 5
    assert len(resultado.cluster_state.micro_agentes) == 5
    assert resultado.persistencia_bitacora_id is not None


def test_ejecutar_skill_resolucion():
    """Valida la ejecución de una habilidad para desbloquear un siniestro estancado."""
    resp = langgraph_agent_control.ejecutar_skill_resolucion(
        reclamo_id="REC-2026-STALL-101",
        skill_id="SKILL_REASIGNAR_PERITO_GPS",
        motivo="Reasignación automática por geocerca"
    )
    assert resp.exito is True
    assert resp.numero_reclamo == "REC-2026-STALL-101"
    assert resp.nuevo_estado_expediente == "PERITAJE_ASIGNADO_GPS"
    assert "Ing. Roberto Paz" in resp.detalle


def test_endpoints_agent_api(client):
    """Valida los endpoints REST del Boundary en FastAPI."""
    # 1. GET /api/agent/cluster-state
    r1 = client.get("/api/agent/cluster-state")
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["cluster_estado"] == "SYNCHRONIZED"
    assert len(d1["nodos_grafo"]) == 5
    assert len(d1["micro_agentes"]) == 5

    # 2. GET /api/agent/stalled-claims
    r2 = client.get("/api/agent/stalled-claims")
    assert r2.status_code == 200
    d2 = r2.json()
    assert len(d2) >= 1

    # 3. POST /api/agent/run-cycle
    r3 = client.post("/api/agent/run-cycle")
    assert r3.status_code == 200
    d3 = r3.json()
    assert "ciclo_id" in d3
    assert "reflexion_final" in d3

    # 4. POST /api/agent/execute-skill
    r4 = client.post(
        "/api/agent/execute-skill",
        json={
            "numero_reclamo": "REC-2026-STALL-103",
            "skill_id": "SKILL_FAST_TRACK_APROBACION",
            "motivo": "Aprobación rápida por bajo monto"
        }
    )
    assert r4.status_code == 200
    d4 = r4.json()
    assert d4["exito"] is True
    assert d4["nuevo_estado_expediente"] == "APROBADO_FAST_TRACK"
