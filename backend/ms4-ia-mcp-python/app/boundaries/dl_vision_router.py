"""
=============================================================================
 AegisCore AI - MS4: [BOUNDARY] Router FastAPI de Visión Artificial Deep Learning
 Caso de Uso 11 (CU11): Analizar Fotografía/Video de Siniestro con Deep Learning
 Red Neuronal Convolucional CrashNet (TensorFlow / Keras)
 Metodología ICONIX - Objeto Boundary (Punto de Entrada HTTP / API REST)
=============================================================================
"""

from typing import List, Dict, Any, Optional
from pathlib import Path as FileSystemPath
from fastapi import APIRouter, Depends, status, HTTPException, Path
from fastapi.responses import FileResponse, RedirectResponse
from app.core.security import require_roles, CurrentUser, get_current_user_optional
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


@router.get(
    "/claim-report-pdf/{reclamo_id}",
    summary="Descargar Dictamen Técnico Pericial Oficial en PDF",
    description="Recupera o redirige a la URL presignada de Amazon S3 del dictamen técnico pericial del siniestro."
)
def download_claim_report_pdf(
    reclamo_id: str = Path(..., description="Identificador del siniestro"),
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional)
):
    """
    Obtiene el PDF del dictamen pericial desde Amazon S3 o el almacenamiento local.
    """
    try:
        from app.services.s3_storage_service import s3_storage_service
        from app.services.inspection_report_pdf_service import REPORTS_DIR

        # 1. Buscar en S3 si está disponible la URL presignada
        cli, veh = crashnet_vision_control.resolver_jerarquia_cliente_vehiculo(numero_reclamo=reclamo_id)
        s3_key = s3_storage_service.construir_s3_key_incidente(
            cliente_id=cli,
            vehiculo_id=veh,
            reclamo_id=reclamo_id,
            categoria="reportes",
            nombre_archivo=f"dictamen_peritaje_tecnico_{reclamo_id}.pdf"
        )

        if s3_storage_service.is_configured and s3_storage_service.existe_objeto(s3_key):
            presigned_url = s3_storage_service.generar_presigned_download_url(s3_key, expiracion_segundos=1800)
            if presigned_url:
                return RedirectResponse(url=presigned_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

        # 2. Si no está en S3 o falla, buscar en almacenamiento local
        matching_files = list(REPORTS_DIR.glob(f"dictamen_peritaje_tecnico_{reclamo_id}*.pdf"))
        if matching_files:
            latest_file = max(matching_files, key=lambda p: p.stat().st_mtime)
            return FileResponse(
                path=str(latest_file),
                media_type="application/pdf",
                filename=latest_file.name
            )

        # 3. Si no existe aún el archivo, forzar el peritaje y generación para el reclamo
        exp = crashnet_vision_control.obtener_expediente_peritaje(reclamo_id)
        if exp and exp.s3_dictamen_pdf_url and exp.s3_dictamen_pdf_url.startswith("http"):
            return RedirectResponse(url=exp.s3_dictamen_pdf_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

        matching_files = list(REPORTS_DIR.glob(f"dictamen_peritaje_tecnico_{reclamo_id}*.pdf"))
        if matching_files:
            latest_file = max(matching_files, key=lambda p: p.stat().st_mtime)
            return FileResponse(
                path=str(latest_file),
                media_type="application/pdf",
                filename=latest_file.name
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dictamen pericial en PDF no encontrado para el reclamo {reclamo_id}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al descargar dictamen pericial en PDF: {str(e)}"
        )
