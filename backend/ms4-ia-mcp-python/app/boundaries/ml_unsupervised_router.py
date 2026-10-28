"""
=============================================================================
 AegisCore AI - MS4: [BOUNDARY] Router FastAPI de Machine Learning No Supervisado
 Caso de Uso 13 (CU13): Segmentar Asegurados por Riesgo y Detectar Fraudes
 Metodología ICONIX - Objeto Boundary (Punto de Entrada HTTP / API REST)
 Integración con K-Means, Isolation Forest y MongoDB Atlas (alertas_fraude_anomalias)
=============================================================================
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status, HTTPException, Path
from app.core.security import require_roles, CurrentUser
from app.entities.ml_unsupervised_dto import (
    ClusterProfileDTO,
    FraudAlertDTO,
    EvaluateClaimInputDTO,
    FraudDashboardSummaryDTO,
    FreezeClaimResponseDTO
)
from app.controls.unsupervised_fraud_control import unsupervised_control

router = APIRouter(
    prefix="/api/ml/unsupervised",
    tags=["CU13 - Machine Learning No Supervisado (K-Means & Isolation Forest)"]
)


@router.get(
    "/clusters-and-anomalies",
    response_model=FraudDashboardSummaryDTO,
    summary="Resumen Consolidado de Segmentación (K-Means) y Detección de Fraude (Isolation Forest)",
    description="Retorna el Threat Index Gauge, monto de pérdidas prevenidas, los 3 clusters descubiertos "
                "por K-Means con su Silhouette Score, y las alertas vivas de fraude recuperadas de MongoDB Atlas."
)
def get_clusters_and_anomalies(
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
) -> FraudDashboardSummaryDTO:
    """
    Ejecuta el método operacional obtenerResumenDashboard() en el Control ICONIX.
    """
    try:
        return unsupervised_control.obtener_resumen_dashboard()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener resumen de segmentación y fraude: {str(e)}"
        )


@router.post(
    "/evaluate-claim",
    response_model=FraudAlertDTO,
    summary="Auditoría de Siniestro en Tiempo Real con Isolation Forest",
    description="Evalúa un siniestro reportado contra el modelo no supervisado Isolation Forest. "
                "Calcula la divergencia contra costos normales de mercado, asigna criticidad "
                "(CRÍTICO, ALTO, MEDIO, NORMAL) y si es anómalo, lo persiste reactivamente en MongoDB Atlas."
)
def evaluate_claim(
    payload: EvaluateClaimInputDTO,
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
) -> FraudAlertDTO:
    """
    Ejecuta el método operacional evaluarAnomaliaReclamo() en el Control ICONIX.
    """
    try:
        return unsupervised_control.evaluar_anomalia_reclamo(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante la evaluación de anomalía del reclamo: {str(e)}"
        )


@router.post(
    "/freeze-claim/{reclamo_id}",
    response_model=FreezeClaimResponseDTO,
    summary="Congelamiento Preventivo de Pago de Siniestro (Intervención SIU)",
    description="Bloquea el desembolso del siniestro en MongoDB Atlas (expedientes_siniestros) "
                "y actualiza su estado a CONGELADO_PREVENTIVO_SAGA para salvaguardar reservas."
)
def freeze_claim_payout(
    reclamo_id: str = Path(..., description="Identificador del siniestro (ej: REC-2026-00402)"),
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
) -> FreezeClaimResponseDTO:
    """
    Ejecuta el método operacional congelarPagoSiniestro() en el Control ICONIX.
    """
    try:
        return unsupervised_control.congelar_pago_siniestro(reclamo_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al congelar preventivamente el reclamo {reclamo_id}: {str(e)}"
        )


@router.get(
    "/alerts",
    response_model=List[FraudAlertDTO],
    summary="Listado de Alertas de Fraude y Anomalías Vivas en MongoDB Atlas",
    description="Recupera las alertas más recientes almacenadas en la colección alertas_fraude_anomalias."
)
def list_fraud_alerts(
    limit: int = 50,
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN", "PERITO", "AUDITOR"]))
) -> List[FraudAlertDTO]:
    """
    Ejecuta el método operacional listarAlertasFraude() en el Control ICONIX.
    """
    try:
        return unsupervised_control.listar_alertas_fraude(limite=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar alertas de fraude: {str(e)}"
        )


@router.post(
    "/retrain",
    summary="Reentrenar K-Means (K=3) e Isolation Forest",
    description="Fuerza el reentrenamiento no supervisado utilizando los datos transaccionales "
                "de Neon PostgreSQL y actualiza los artefactos en disco."
)
def retrain_unsupervised_models(
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN"]))
) -> Dict[str, Any]:
    """
    Ejecuta el método operacional entrenarModelosNoSupervisados() en el Control ICONIX.
    """
    try:
        unsupervised_control.entrenar_modelos_no_supervisados()
        return {
            "status": "SUCCESS",
            "message": "Modelos K-Means e Isolation Forest reentrenados exitosamente.",
            "silhouette_score": unsupervised_control.silhouette_score_val,
            "clusters_identificados": len(unsupervised_control.cluster_profiles)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el reentrenamiento no supervisado: {str(e)}"
        )
