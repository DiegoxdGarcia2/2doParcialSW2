"""
=============================================================================
 AegisCore AI - MS4: Pruebas Automatizadas para Analítica Comercial 360° y MCP
 Suite de pruebas Pytest: Control ICONIX, Servidor MCP y Router FastAPI
=============================================================================
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.controls.commercial_analytics_control import commercial_control
from app.entities.commercial_analytics_dto import CommercialFilterInputDTO
from app.mcp_voice_reports.server.mcp_protocol_server import McpProtocolServer


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_mcp_tool_catalog_includes_commercial_360():
    """Valida que el catálogo MCP contenga la tool tipada tool_analitica_comercial_360."""
    tools = McpProtocolServer.list_tools()
    tool_names = [t.name for t in tools]
    assert "tool_analitica_comercial_360" in tool_names
    commercial_tool = next(t for t in tools if t.name == "tool_analitica_comercial_360")
    assert "departamento" in commercial_tool.inputSchema["properties"]
    assert "ramo" in commercial_tool.inputSchema["properties"]
    assert "canal" in commercial_tool.inputSchema["properties"]


def test_commercial_control_analysis_default():
    """Valida el cálculo de KPIs comerciales base (LTV, CAC, Churn, Conversión)."""
    filtros = CommercialFilterInputDTO(
        departamento="TODOS",
        ramo="TODOS",
        canal="TODOS",
        periodo="Q3"
    )
    res = commercial_control.analizar_rentabilidad_comercial_360(filtros)
    assert res is not None
    assert res.prima_media_usd > 200.0
    assert res.cac_promedio_usd > 50.0
    assert res.ltv_promedio_usd > res.cac_promedio_usd
    assert res.ltv_cac_ratio >= 3.0, f"LTV/CAC ratio ({res.ltv_cac_ratio}) debe ser saludable"
    assert 4.0 <= res.churn_anual_pct <= 20.0
    assert len(res.canales_eficiencia) == 4
    assert len(res.tendencia_mensual) == 12


def test_commercial_control_analysis_filtered_region():
    """Valida la reactividad de métricas al filtrar por Santa Cruz y canal WhatsApp."""
    filtros = CommercialFilterInputDTO(
        departamento="SANTA_CRUZ",
        ramo="VEHICULAR",
        canal="WHATSAPP_N8N",
        periodo="YTD"
    )
    res = commercial_control.analizar_rentabilidad_comercial_360(filtros)
    assert res.filtros_aplicados.departamento == "SANTA_CRUZ"
    assert len(res.canales_eficiencia) == 1
    assert res.canales_eficiencia[0].codigo_canal == "WHATSAPP_N8N"


def test_endpoint_commercial_analytics(client):
    """Prueba HTTP del endpoint POST /api/commercial/analytics."""
    payload = {
        "departamento": "LA_PAZ",
        "ramo": "TODOS",
        "canal": "WEB_REACT",
        "periodo": "Q3"
    }
    response = client.post("/api/commercial/analytics", json=payload)
    assert response.status_code == 200, f"Error HTTP: {response.text}"
    data = response.json()
    assert "prima_media_usd" in data
    assert "cac_promedio_usd" in data
    assert "ltv_cac_ratio" in data
    assert "canales_eficiencia" in data
    assert "tendencia_mensual" in data


def test_endpoint_filters_metadata(client):
    """Prueba HTTP del endpoint GET /api/commercial/filters-metadata."""
    response = client.get("/api/commercial/filters-metadata")
    assert response.status_code == 200
    data = response.json()
    assert "departamentos" in data
    assert "ramos" in data
    assert "canales" in data
    assert "periodos" in data
    assert len(data["departamentos"]) >= 5

