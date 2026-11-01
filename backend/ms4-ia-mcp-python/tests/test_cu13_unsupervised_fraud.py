"""
=============================================================================
 AegisCore AI - MS4: Pruebas Automatizadas para CU13 (K-Means & Isolation Forest)
 Suite de pruebas Pytest: Control ICONIX, Pipeline No Supervisado, MongoDB Atlas
 y Router FastAPI
=============================================================================
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.controls.unsupervised_fraud_control import unsupervised_control
from app.entities.ml_unsupervised_dto import EvaluateClaimInputDTO


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_kmeans_clustering_segments_and_silhouette():
    """
    Valida que K-Means descubra 3 clusters y que el Silhouette Score
    sea válido (> 0.25 para datos actuariales continuos).
    """
    if not unsupervised_control.cluster_profiles:
        unsupervised_control.entrenar_modelos_no_supervisados()

    profiles = unsupervised_control.cluster_profiles
    assert len(profiles) == 3, f"Se esperaban 3 clusters pero se obtuvieron {len(profiles)}"
    
    total_asegurados = sum(p.total_asegurados for p in profiles)
    assert total_asegurados == 1200, f"La suma de asegurados ({total_asegurados}) debe ser 1,200"

    pct_total = sum(p.porcentaje_flota for p in profiles)
    assert 99.0 <= pct_total <= 101.0, f"El porcentaje total ({pct_total}%) debe sumar ~100%"

    assert unsupervised_control.silhouette_score_val > 0.25, (
        f"Silhouette score ({unsupervised_control.silhouette_score_val}) debe ser > 0.25"
    )

    # Validar que los 3 perfiles tengan nombres de negocio
    nombres = [p.nombre for p in profiles]
    assert any("Bajo Riesgo" in n or "Prudentes" in n for n in nombres)
    assert any("Moderado" in n for n in nombres)
    assert any("Alta Siniestralidad" in n for n in nombres)


def test_isolation_forest_normal_claim():
    """
    Valida que un reclamo típico y coherente con el mercado no sea marcado
    como anomalía crítica.
    """
    normal_claim = EvaluateClaimInputDTO(
        reclamo_id="REC-TEST-NORMAL-001",
        poliza_id="POL-2026-AUT-10001",
        edad_conductor=42,
        tipo_vehiculo="SUV",
        valor_comercial_usd=28000.0,
        monto_solicitado_usd=1200.0,
        dias_desde_emision=120,
        historial_siniestros=0,
        taller_mecanico="Taller Oficial Autorizado"
    )

    alerta = unsupervised_control.evaluar_anomalia_reclamo(normal_claim)
    assert alerta is not None
    assert alerta.reclamo_id == "REC-TEST-NORMAL-001"
    assert alerta.nivel_criticidad in ["NORMAL", "MEDIO"]
    assert alerta.estado_pago in ["APROBADO_FAST_TRACK", "PENDIENTE_REVISION"]
    assert alerta.monto_solicitado_usd == 1200.0


def test_isolation_forest_anomalous_fraud_claim():
    """
    Valida que un reclamo fraudulento (sobreprecio severo tras 3 días de emisión)
    sea marcado como anómalo, nivel CRÍTICO y propuesto para congelamiento.
    """
    fraud_claim = EvaluateClaimInputDTO(
        reclamo_id="REC-TEST-FRAUD-999",
        poliza_id="POL-2026-AUT-99999",
        edad_conductor=21,
        tipo_vehiculo="SEDAN",
        valor_comercial_usd=12000.0,
        monto_solicitado_usd=9800.0,  # ~82% del valor del auto
        dias_desde_emision=3,        # Solo 3 días tras emisión
        historial_siniestros=3,
        taller_mecanico="Taller Clandestino El Rápido"
    )

    alerta = unsupervised_control.evaluar_anomalia_reclamo(fraud_claim)
    assert alerta is not None
    assert alerta.reclamo_id == "REC-TEST-FRAUD-999"
    assert alerta.es_anomalo is True
    assert alerta.nivel_criticidad in ["CRÍTICO", "ALTO"]
    assert alerta.divergencia_porcentaje > 100.0
    assert alerta.score_anomalia < 0.0


def test_congelar_pago_siniestro_mongo():
    """
    Valida el congelamiento preventivo de pago del siniestro (acción SIU).
    """
    resultado = unsupervised_control.congelar_pago_siniestro("REC-TEST-FRAUD-999")
    assert resultado is not None
    assert resultado.reclamo_id == "REC-TEST-FRAUD-999"
    assert resultado.nuevo_estado == "CONGELADO_PREVENTIVO_SAGA"
    assert "congelada preventivamente" in resultado.mensaje.lower()


def test_endpoint_clusters_and_anomalies(client):
    """
    Valida el endpoint GET /api/ml/unsupervised/clusters-and-anomalies.
    """
    response = client.get("/api/ml/unsupervised/clusters-and-anomalies")
    assert response.status_code == 200
    data = response.json()
    assert "threat_index_percentage" in data
    assert "clusters_kmeans" in data
    assert len(data["clusters_kmeans"]) == 3
    assert "alertas_recientes" in data
    assert data["silhouette_score_kmeans"] > 0.25


def test_endpoint_evaluate_and_freeze(client):
    """
    Valida los endpoints POST /api/ml/unsupervised/evaluate-claim y
    POST /api/ml/unsupervised/freeze-claim/{reclamo_id}.
    """
    payload = {
        "reclamo_id": "REC-API-TEST-888",
        "poliza_id": "POL-2026-AUT-88888",
        "edad_conductor": 24,
        "tipo_vehiculo": "SEDAN",
        "valor_comercial_usd": 15000.0,
        "monto_solicitado_usd": 11500.0,
        "dias_desde_emision": 4,
        "historial_siniestros": 2,
        "taller_mecanico": "Taller AutoExpertos"
    }
    
    # 1. Evaluar siniestro
    eval_resp = client.post("/api/ml/unsupervised/evaluate-claim", json=payload)
    assert eval_resp.status_code == 200
    alerta_data = eval_resp.json()
    assert alerta_data["reclamo_id"] == "REC-API-TEST-888"
    assert alerta_data["es_anomalo"] is True

    # 2. Congelar pago
    freeze_resp = client.post("/api/ml/unsupervised/freeze-claim/REC-API-TEST-888")
    assert freeze_resp.status_code == 200
    freeze_data = freeze_resp.json()
    assert freeze_data["reclamo_id"] == "REC-API-TEST-888"
    assert freeze_data["nuevo_estado"] == "CONGELADO_PREVENTIVO_SAGA"
    assert freeze_data["score_anomalia"] == alerta_data["score_anomalia"], (
        f"El score dinámico en freeze ({freeze_data['score_anomalia']}) debe coincidir con el score evaluado ({alerta_data['score_anomalia']})"
    )


def test_vehicular_category_validation_cu13_security(client):
    """
    Seguridad Pydantic v2: Rechazo de categorías vehiculares arbitrarias (HTTP 422).
    """
    payload_invalido = {
        "reclamo_id": "REC-TEST-INVALID-001",
        "poliza_id": "POL-2026-AUT-00000",
        "edad_conductor": 30,
        "tipo_vehiculo": "OVNI_INTERGALACTICO",
        "valor_comercial_usd": 20000.0,
        "monto_solicitado_usd": 5000.0,
        "dias_desde_emision": 30,
        "historial_siniestros": 0
    }
    response = client.post("/api/ml/unsupervised/evaluate-claim", json=payload_invalido)
    assert response.status_code == 422, f"Se esperaba 422 pero se obtuvo {response.status_code}"


def test_endpoint_aliases_and_dynamic_headers_cu13(client):
    """
    Verifica alias /detect-fraud y dinamismo en cabeceras de /clusters-and-anomalies.
    """
    payload = {
        "reclamo_id": "REC-API-ALIAS-007",
        "poliza_id": "POL-2026-AUT-77777",
        "edad_conductor": 22,
        "tipo_vehiculo": "HATCHBACK",
        "valor_comercial_usd": 14000.0,
        "monto_solicitado_usd": 11000.0,
        "dias_desde_emision": 2,
        "historial_siniestros": 2,
        "taller_mecanico": "Taller Express"
    }
    res_detect = client.post("/api/ml/unsupervised/detect-fraud", json=payload)
    assert res_detect.status_code == 200
    assert "score_anomalia" in res_detect.json()

    # Verificar cabeceras dinámicas
    dash_resp = client.get("/api/ml/unsupervised/clusters-and-anomalies")
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    assert dash_data["threat_level_label"] in ["BAJO", "MODERADO", "ALTO", "CRÍTICO"]
    assert dash_data["total_siniestros_auditados"] >= 1200
    assert isinstance(dash_data["threat_index_percentage"], (int, float))
    assert isinstance(dash_data["perdidas_prevenidas_usd"], (int, float))
