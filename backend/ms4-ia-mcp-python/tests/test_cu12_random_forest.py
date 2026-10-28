"""
=============================================================================
 AegisCore AI - MS4: Pruebas Automatizadas para CU12 (Random Forest)
 Suite de pruebas Pytest: Control ICONIX, Pipeline ML y Router FastAPI
=============================================================================
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.controls.random_forest_service import actuarial_control
from app.entities.ml_supervised_dto import PredictionInputDTO


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_cargar_dataset_historico():
    """Valida la lectura de los 1,200 registros de Neon PostgreSQL."""
    df = actuarial_control.cargar_dataset_historico()
    assert len(df) == 1200, f"Se esperaban 1,200 registros pero se obtuvieron {len(df)}"
    expected_cols = [
        "edad_asegurado",
        "antiguedad_licencia_anios",
        "tipo_vehiculo",
        "valor_comercial_usd",
        "prima_anual_calculada",
        "tuvo_siniestro_en_anio",
        "polizas_vendidas_en_mes"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Columna {col} no encontrada en el dataset"


def test_metricas_calidad_random_forest():
    """Valida que el modelo cumpla los umbrales de precisión actuarial."""
    metrics = actuarial_control.obtener_metricas_y_feature_importances()
    assert metrics is not None
    assert metrics.r2_score >= 0.85, f"R^2 ({metrics.r2_score}) es inferior al umbral 0.85"
    assert metrics.mae_usd > 0.0, "MAE debe ser mayor a 0"
    assert metrics.accuracy_siniestros >= 0.75, f"Exactitud ({metrics.accuracy_siniestros}) inferior a 0.75"
    assert len(metrics.feature_importances) > 0, "Debe incluir ponderación de variables (XAI)"


def test_inferencia_actuarial_reglas_negocio():
    """Valida la inferencia completa y coherencia del intervalo del 95%."""
    payload = PredictionInputDTO(
        edad_asegurado=45,
        antiguedad_licencia_anios=20,
        tipo_vehiculo="SUV",
        anio_vehiculo=2022,
        valor_comercial_usd=32000.0,
        historial_siniestros_previos=0,
        perfil_riesgo_score=25.0,
        meses_a_proyectar=4
    )
    resultado = actuarial_control.predecir_prima_optima_y_demanda(payload)

    assert resultado.prima_anual_optima_usd > 300.0
    assert len(resultado.rango_confianza_95) == 2
    assert resultado.rango_confianza_95[0] <= resultado.prima_anual_optima_usd <= resultado.rango_confianza_95[1]
    assert resultado.nivel_riesgo_clasificado in ["BAJO", "MEDIO", "ALTO", "CRÍTICO"]
    assert len(resultado.proyecciones_mensuales) == 4
    for proj in resultado.proyecciones_mensuales:
        assert proj.ventas_estimadas_polizas > 0
        assert proj.prima_sugerida_usd > 0.0


def test_endpoint_predict_sales_and_premium(client):
    """Prueba de integración HTTP contra el endpoint FastAPI."""
    payload = {
        "edad_asegurado": 28,
        "antiguedad_licencia_anios": 5,
        "tipo_vehiculo": "HATCHBACK",
        "anio_vehiculo": 2018,
        "valor_comercial_usd": 15000.0,
        "historial_siniestros_previos": 1,
        "perfil_riesgo_score": 50.0,
        "meses_a_proyectar": 3
    }
    response = client.post("/api/ml/predict-sales-and-premium", json=payload)
    assert response.status_code == 200, f"Error HTTP: {response.text}"
    data = response.json()
    assert "prima_anual_optima_usd" in data
    assert "rango_confianza_95" in data
    assert "probabilidad_siniestro_pct" in data
    assert len(data["proyecciones_mensuales"]) == 3


def test_endpoint_model_metrics(client):
    """Prueba del endpoint de consulta de métricas e interpretabilidad."""
    response = client.get("/api/ml/model-metrics")
    assert response.status_code == 200
    data = response.json()
    assert "r2_score" in data
    assert "feature_importances" in data
    assert len(data["feature_importances"]) > 0


def test_endpoint_dataset_sample(client):
    """Prueba de consulta de muestra de dataset."""
    response = client.get("/api/ml/dataset-sample?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert "prima_anual_calculada" in data[0]
