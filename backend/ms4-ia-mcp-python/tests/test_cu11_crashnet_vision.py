"""
=============================================================================
 AegisCore AI - MS4: Pruebas Automatizadas para CU11 (Deep Learning CrashNet)
 Suite de pruebas Pytest: Control ICONIX, Pipeline CNN, MongoDB Atlas
 y Router FastAPI
=============================================================================
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pytest
import numpy as np
from fastapi.testclient import TestClient
from app.main import app
from app.controls.crashnet_vision_control import crashnet_vision_control
from app.entities.dl_vision_dto import DamageAnalysisInputDTO


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_preprocesar_imagen_tensor():
    """Valida la normalización de la imagen a tensor 224x224x3."""
    tensor = crashnet_vision_control.preprocesar_imagen_tensor(None)
    assert tensor is not None
    assert tensor.shape == (1, 224, 224, 3)
    assert tensor.min() >= 0.0
    assert tensor.max() <= 1.0


def test_detectar_piezas_averiadas():
    """Valida la detección multi-cabezal de componentes averiados y códigos OEM."""
    tensor = np.zeros((1, 224, 224, 3), dtype=np.float32)
    piezas = crashnet_vision_control.detectar_piezas_averiadas(tensor, "FRONTAL")
    
    assert len(piezas) >= 3
    piezas_nombres = [p.parte_id for p in piezas]
    assert "bumper" in piezas_nombres
    assert "headlamp" in piezas_nombres
    assert "hood" in piezas_nombres

    for p in piezas:
        assert p.confianza_deteccion >= 0.85
        assert p.porcentaje_severidad > 0.0
        assert p.codigo_oem.startswith("OEM #")
        assert p.costo_total_usd > 0.0
        assert p.bounding_box is not None
        assert p.bounding_box.polygon_points is not None


def test_calcular_severidad_y_estimar_costos():
    """Valida el cálculo de gravedad global y desglose financiero con deducible."""
    piezas = crashnet_vision_control.detectar_piezas_averiadas(np.zeros((1, 224, 224, 3)), "FRONTAL")
    gravedad, score = crashnet_vision_control.calcular_severidad_estructural(piezas)
    
    assert gravedad in ["LEVE", "MEDIA", "GRAVE", "PÉRDIDA_TOTAL"]
    assert 0.0 <= score <= 1.0

    liquidacion = crashnet_vision_control.estimar_costo_reparacion(piezas)
    assert liquidacion.costo_repuestos_usd > 0.0
    assert liquidacion.costo_mano_obra_usd > 0.0
    assert liquidacion.costo_total_reparacion_usd == liquidacion.costo_repuestos_usd + liquidacion.costo_mano_obra_usd
    assert liquidacion.deducible_calculado_usd == 250.00
    assert liquidacion.monto_indemnizable_neto_usd == liquidacion.costo_total_reparacion_usd - 250.00


def test_persistir_peritaje_mongodb():
    """Valida la actualización del expediente en MongoDB Atlas con el triaje IA."""
    input_dto = DamageAnalysisInputDTO(
        numero_reclamo="REC-2026-00492",
        numero_poliza="POL-2026-AUT-00892",
        angulo_toma="FRONTAL_CUARTO_DERECHO",
        modelo_vehiculo="Tesla Model Y Long Range"
    )
    assessment = crashnet_vision_control.analizar_fotografia_siniestro(input_dto)
    assert assessment is not None
    assert assessment.numero_reclamo == "REC-2026-00492"
    assert assessment.gravedad_global == "MEDIA"
    assert len(assessment.piezas_averiadas) >= 3


def test_api_detect_damage_endpoint(client):
    """Valida el endpoint HTTP POST /api/dl/detect-damage."""
    payload = {
        "numero_reclamo": "REC-2026-00492",
        "numero_poliza": "POL-2026-AUT-00892",
        "angulo_toma": "FRONTAL_CUARTO_DERECHO",
        "modelo_vehiculo": "Tesla Model Y Long Range 2024"
    }
    response = client.post("/api/dl/detect-damage", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["numero_reclamo"] == "REC-2026-00492"
    assert data["modelo_deep_learning"] == "TensorFlow-CrashNet-CNN-v2.1"
    assert "piezas_averiadas" in data
    assert len(data["piezas_averiadas"]) >= 3
    assert "liquidacion_financiera" in data
    assert data["liquidacion_financiera"]["deducible_calculado_usd"] == 250.00


def test_api_confirm_assessment_and_liquidate(client):
    """Valida la confirmación de peritaje y transferencia a la Saga de liquidación."""
    response = client.post("/api/dl/confirm-assessment/REC-2026-00492")
    assert response.status_code == 200
    data = response.json()
    assert data["numero_reclamo"] == "REC-2026-00492"
    assert data["nuevo_estado"] == "EN_PROCESO_LIQUIDACION"
    assert "transferido a la saga" in data["mensaje"].lower()
