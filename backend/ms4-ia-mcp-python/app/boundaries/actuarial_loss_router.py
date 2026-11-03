"""
=============================================================================
 AegisCore AI - MS4: [BOUNDARY] Router FastAPI de Siniestralidad y Riesgo 360°
 Metodología ICONIX - Objeto Boundary (Punto de Entrada HTTP / API REST)
 Orquesta la invocación de la Tool MCP 'tool_analitica_siniestralidad_360'
 Consultas 100% SQL Puras sobre dataset_historico_ml_polizas en PostgreSQL Neon
=============================================================================
"""

from fastapi import APIRouter, Depends, status, HTTPException
from app.core.security import require_roles, CurrentUser
from app.entities.actuarial_loss_dto import (
    ActuarialLossFilterInputDTO,
    ActuarialLossSummaryDTO,
    ActuarialFilterOptionsDTO
)
from app.controls.actuarial_loss_control import actuarial_loss_control
from app.mcp_voice_reports.server.mcp_protocol_server import McpProtocolServer

router = APIRouter(
    prefix="/api/actuarial/loss",
    tags=["Siniestralidad & Riesgo Demográfico 360° (PostgreSQL SQL Puro)"]
)


@router.post(
    "/analytics",
    response_model=ActuarialLossSummaryDTO,
    summary="Obtener Métricas 360° de Siniestralidad, Severidad y Riesgo Actuarial",
    description="Ejecuta consultas agregadas SQL 100% puras sobre los 1,200 registros de dataset_historico_ml_polizas "
                "en Neon PostgreSQL, calculando frecuencia, severidad, loss ratio y desglose demográfico."
)
def get_actuarial_loss_analytics(
    payload: ActuarialLossFilterInputDTO,
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
) -> ActuarialLossSummaryDTO:
    """Invoca la lógica de análisis actuarial de siniestralidad real."""
    try:
        return actuarial_loss_control.analizar_siniestralidad_actuarial_360(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar analítica actuarial de siniestralidad: {str(e)}"
        )


@router.get(
    "/filters-metadata",
    response_model=ActuarialFilterOptionsDTO,
    summary="Obtener Catálogo de Opciones para la Barra de Filtros Actuariales 360°",
    description="Retorna las listas de tipos de vehículo, rangos de edad, experiencia de licencia y año de vehículo."
)
def get_loss_filters_metadata(
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
) -> ActuarialFilterOptionsDTO:
    """Retorna los metadatos de configuración de filtros actuariales."""
    try:
        return actuarial_loss_control.obtener_opciones_filtros()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener metadatos de filtros actuariales: {str(e)}"
        )

