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


def test_vehiculo_intacto_cero_danos():
    """Valida que una fotografia de vehiculo intacto (sin colision) retorne 0 piezas y $0 USD."""
    from PIL import Image
    import io, base64

    # Crear imagen plana / uniforme simulando vehiculo impecable sin danos
    img_clean = Image.new('RGB', (224, 224), color=(225, 230, 235))
    buf = io.BytesIO()
    img_clean.save(buf, format='JPEG')
    b64_clean = base64.b64encode(buf.getvalue()).decode('utf-8')

    input_dto = DamageAnalysisInputDTO(
        numero_reclamo='REC-FOTO-CLEAN-01',
        numero_poliza='POL-2026-AUT-99999',
        imagen_base64=f'data:image/jpeg;base64,{b64_clean}',
        modelo_vehiculo='Toyota Prius 2024 (Vehiculo Intacto)'
    )
    assessment = crashnet_vision_control.analizar_fotografia_siniestro(input_dto)
    assert assessment is not None
    assert assessment.vehiculo_intacto is True
    assert len(assessment.piezas_averiadas) == 0
    assert assessment.score_danos_global == 0.0
    assert assessment.gravedad_global == 'LEVE'
    assert assessment.liquidacion_financiera.costo_total_reparacion_usd == 0.0
    assert assessment.liquidacion_financiera.monto_indemnizable_neto_usd == 0.0


def test_imagen_personalizada_dinamica_base64():
    """Valida la segmentacion adaptativa y calculo dinamico de poligonos SVG ante impacto."""
    from PIL import Image
    import io, base64

    # Crear imagen con dano marcado en el parachoques inferior
    img_crash = Image.new('RGB', (224, 224), color=(220, 220, 220))
    arr = np.array(img_crash)
    # Inyectar textura de impacto caotico en el tercio inferior
    rng = np.random.RandomState(42)
    arr[120:200, 30:160] = rng.randint(10, 240, size=(80, 130, 3), dtype=np.uint8)
    img_crash = Image.fromarray(arr)

    buf = io.BytesIO()
    img_crash.save(buf, format='JPEG')
    b64_crash = base64.b64encode(buf.getvalue()).decode('utf-8')

    input_dto = DamageAnalysisInputDTO(
        numero_reclamo='REC-FOTO-CRASH-02',
        numero_poliza='POL-2026-AUT-88888',
        imagen_base64=b64_crash,
        modelo_vehiculo='Honda Civic 2023 (Impacto Frontal)'
    )
    assessment = crashnet_vision_control.analizar_fotografia_siniestro(input_dto)
    assert assessment is not None
    assert assessment.vehiculo_intacto is False
    assert len(assessment.piezas_averiadas) >= 1
    # Verificar que el parachoques tenga coordenadas dinamicas de poligono SVG
    bumper = next((p for p in assessment.piezas_averiadas if p.parte_id == 'bumper'), None)
    assert bumper is not None
    assert bumper.bounding_box is not None
    assert bumper.bounding_box.polygon_points is not None
    assert len(bumper.bounding_box.polygon_points.split()) == 4


def test_tensorflow_deep_learning_model_loaded_and_predicts():
    """Valida que el modelo TensorFlow CrashNet CNN esté cargado y realice inferencia por tensores."""
    assert crashnet_vision_control.tf_model is not None
    sample_tensor = np.random.uniform(0.0, 1.0, size=(1, 224, 224, 3)).astype(np.float32)
    clase, confianza = crashnet_vision_control.predecir_severidad_convolucional(sample_tensor)
    assert clase in ["LEVE", "MODERADO", "GRAVE", "PERDIDA_TOTAL"]
    assert 0.0 <= confianza <= 1.0

