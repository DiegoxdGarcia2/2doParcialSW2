"""
=============================================================================
 Pruebas Automatizadas: Analítica de Siniestralidad y Riesgo Demográfico 360°
 Metodología ICONIX - Verificación de Control, Boundary y Persistencia Real PostgreSQL
=============================================================================
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.entities.actuarial_loss_dto import ActuarialLossFilterInputDTO
from app.controls.actuarial_loss_control import actuarial_loss_control
from app.mcp_voice_reports.server.mcp_protocol_server import McpProtocolServer


def test_actuarial_filter_options():
    """Verifica que el catálogo de filtros retorne opciones completas y coherentes."""
    opts = actuarial_loss_control.obtener_opciones_filtros()
    assert len(opts.tipos_vehiculo) >= 6
    assert len(opts.rangos_edad) >= 6
    assert len(opts.antiguedades_licencia) >= 4
    assert len(opts.antiguedades_vehiculo) >= 4


def test_actuarial_loss_control_default():
    """Verifica el cálculo de KPIs globales sobre los 1,200 registros reales en PostgreSQL."""
    filtros = ActuarialLossFilterInputDTO()
    res = actuarial_loss_control.analizar_siniestralidad_actuarial_360(filtros)

    assert res.total_polizas == 1200
    assert res.total_siniestros > 300  # En el dataset real son 322
    assert 25.0 <= res.frecuencia_siniestralidad_pct <= 30.0  # 26.83% real
    assert res.severidad_media_usd > 2000.0  # ~$2,544 USD real
    assert res.prima_media_anual_usd > 800.0  # ~$1,050 USD real
    assert len(res.desglose_por_vehiculo) == 5  # SUV, Camioneta, Hatchback, Moto, Sedan
    assert len(res.cohortes_edad) == 5  # 18-25, 26-35, 36-50, 51-65, 65+
    assert len(res.tendencia_mensual) >= 12  # 12 meses cronológicos


def test_actuarial_loss_filtered_by_vehicle():
    """Verifica la filtración SQL parametrizada por categoría de vehículo (ej: CAMIONETA)."""
    filtros = ActuarialLossFilterInputDTO(tipo_vehiculo="CAMIONETA")
    res = actuarial_loss_control.analizar_siniestralidad_actuarial_360(filtros)

    assert res.total_polizas == 240
    assert res.total_siniestros == 72
    assert res.frecuencia_siniestralidad_pct == 30.0
    assert len(res.desglose_por_vehiculo) == 1
    assert res.desglose_por_vehiculo[0].tipo_vehiculo == "CAMIONETA"


def test_actuarial_loss_filtered_by_age():
    """Verifica la filtración SQL parametrizada por cohorte joven (18 a 25 años)."""
    filtros = ActuarialLossFilterInputDTO(rango_edad="18-25")
    res = actuarial_loss_control.analizar_siniestralidad_actuarial_360(filtros)

    assert res.total_polizas == 174
    assert res.total_siniestros == 56
    assert 31.0 <= res.frecuencia_siniestralidad_pct <= 33.0  # 32.18% real


def test_endpoint_actuarial_loss_analytics():
    """Verifica la respuesta HTTP del endpoint FastAPI con autenticación y validación de esquema."""
    client = TestClient(app)
    payload = {
        "tipo_vehiculo": "SUV",
        "rango_edad": "TODOS",
        "antiguedad_licencia": "TODOS",
        "antiguedad_vehiculo": "TODOS"
    }
    response = client.post("/api/actuarial/loss/analytics", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_polizas"] == 240
    assert "frecuencia_siniestralidad_pct" in data
    assert "desglose_por_vehiculo" in data
    assert "cohortes_edad" in data
    assert "tendencia_mensual" in data


def test_mcp_tool_invocation_siniestralidad():
    """Verifica la ejecución de la Tool MCP tipada tool_analitica_siniestralidad_360."""
    args = {"tipo_vehiculo": "TODOS", "rango_edad": "TODOS"}
    titulo, kpis, cols, filas, traza = McpProtocolServer.call_tool("tool_analitica_siniestralidad_360", args)

    assert "Siniestralidad" in titulo
    assert "Frecuencia de Siniestralidad" in kpis
    assert len(filas) == 5  # 5 tipos de vehículos
    assert traza.status == "SUCCESS"
    assert "dataset_historico_ml_polizas" in traza.fuente_datos

