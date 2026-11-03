"""
=============================================================================
 AegisCore AI - MS4: [BOUNDARY] Router FastAPI de Analítica Comercial 360°
 Metodología ICONIX - Objeto Boundary (Punto de Entrada HTTP / API REST)
 Orquesta la invocación de la Tool MCP tipada 'tool_analitica_comercial_360'
=============================================================================
"""

from fastapi import APIRouter, Depends, status, HTTPException
from app.core.security import require_roles, CurrentUser
from app.entities.commercial_analytics_dto import (
    CommercialFilterInputDTO,
    CommercialKpiSummaryDTO,
    FilterOptionsDTO
)
from app.controls.commercial_analytics_control import commercial_control
from app.mcp_voice_reports.server.mcp_protocol_server import McpProtocolServer

router = APIRouter(
    prefix="/api/commercial",
    tags=["Analítica Comercial 360° & Rentabilidad (MCP + GraphQL)"]
)


@router.post(
    "/analytics",
    response_model=CommercialKpiSummaryDTO,
    summary="Obtener Métricas 360° de Rentabilidad Comercial y Eficiencia de Canales",
    description="Invoca la Tool MCP tool_analitica_comercial_360 ejecutando consultas sobre Neon PostgreSQL "
                "y aplicando modelos Scikit-Learn para LTV, CAC, Churn y conversión según los filtros dados."
)
def get_commercial_analytics(
    payload: CommercialFilterInputDTO,
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
) -> CommercialKpiSummaryDTO:
    """Ejecuta la Tool MCP tipada de analítica comercial 360°."""
    try:
        resultado = McpProtocolServer.ejecutar_tool_analitica_comercial_360(payload)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar analítica comercial 360°: {str(e)}"
        )


@router.get(
    "/filters-metadata",
    response_model=FilterOptionsDTO,
    summary="Obtener Catálogo de Opciones para la Barra de Filtros 360°",
    description="Retorna las listas de departamentos, ramos, canales y periodos disponibles."
)
def get_filters_metadata(
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
) -> FilterOptionsDTO:
    """Retorna los metadatos de configuración de filtros."""
    try:
        return commercial_control.obtener_opciones_filtros()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener metadatos de filtros: {str(e)}"
        )

