"""
=============================================================================
 AegisCore AI - MS4: [BOUNDARY] Router FastAPI de Visión Artificial Deep Learning
 Caso de Uso 11 (CU11): Analizar Fotografía/Video de Siniestro con Deep Learning
 Red Neuronal Convolucional CrashNet (TensorFlow / Keras)
 Metodología ICONIX - Objeto Boundary (Punto de Entrada HTTP / API REST)
=============================================================================
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status, HTTPException, Path
from app.core.security import require_roles, CurrentUser
from app.entities.dl_vision_dto import (
    DamageAnalysisInputDTO,
    DamageAssessmentOutputDTO,
    ConfirmAssessmentResponseDTO
)
from app.controls.crashnet_vision_control import crashnet_vision_control

router = APIRouter(
    prefix="/api/dl",
    tags=["CU11 - Deep Learning Visión Artificial (TensorFlow CrashNet)"]
)


@router.post(
    "/detect-damage",
    response_model=DamageAssessmentOutputDTO,
    summary="Analizar Fotografía de Siniestro con Red Convolucional CrashNet",
    description="Procesa una imagen de colisión, detecta piezas averiadas, calcula el porcentaje "
                "de severidad estructural y genera la estimación de costos OEM persistiendo el resultado en MongoDB Atlas."
)
def detect_damage(
    payload: DamageAnalysisInputDTO,
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
) -> DamageAssessmentOutputDTO:
    """
    Ejecuta el método operacional analizarFotografiaSiniestro() en el Control ICONIX.
    """
    try:
        return crashnet_vision_control.analizar_fotografia_siniestro(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el análisis visual de colisión: {str(e)}"
        )


@router.get(
    "/claim-damages/{reclamo_id}",
    response_model=DamageAssessmentOutputDTO,
    summary="Obtener Peritaje Visual y Estimación de Daños de un Siniestro",
    description="Recupera el expediente de peritaje técnico de MongoDB Atlas para un reclamo dado."
)
def get_claim_damages(
    reclamo_id: str = Path(..., description="Identificador del siniestro (ej: REC-2026-00492)"),
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
) -> DamageAssessmentOutputDTO:
    """
    Ejecuta el método operacional obtenerExpedientePeritaje() en el Control ICONIX.
    """
    try:
        return crashnet_vision_control.obtener_expediente_peritaje(reclamo_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al recuperar expediente de peritaje para {reclamo_id}: {str(e)}"
        )


@router.post(
    "/confirm-assessment/{reclamo_id}",
    response_model=ConfirmAssessmentResponseDTO,
    summary="Confirmar Peritaje Técnico y Transferir a Liquidación (Saga)",
    description="Asienta el peritaje en MongoDB Atlas como PERITAJE_COMPLETADO y transiciona el "
                "siniestro a EN_PROCESO_LIQUIDACION para su procesamiento en la Saga de 3 microservicios."
)
def confirm_assessment(
    reclamo_id: str = Path(..., description="Identificador del siniestro (ej: REC-2026-00492)"),
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
) -> ConfirmAssessmentResponseDTO:
    """
    Ejecuta el método operacional confirmarPeritajeYLiquidar() en el Control ICONIX.
    """
    try:
        return crashnet_vision_control.confirmar_peritaje_y_liquidar(reclamo_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al confirmar el peritaje de {reclamo_id}: {str(e)}"
        )
