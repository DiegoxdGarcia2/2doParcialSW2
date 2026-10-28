"""
=============================================================================
 AegisCore AI - MS4: [BOUNDARY] Router FastAPI de Machine Learning Supervisado
 Caso de Uso 12 (CU12): Predecir Siniestralidad, Ventas de Pólizas y Prima Óptima
 Metodología ICONIX - Objeto Boundary (Punto de Entrada HTTP / API REST)
=============================================================================
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status, HTTPException
from app.core.security import require_roles, CurrentUser
from app.entities.ml_supervised_dto import (
    PredictionInputDTO,
    PredictionOutputDTO,
    ModelMetricsDTO,
    RetrainResponseDTO
)
from app.controls.random_forest_service import actuarial_control

router = APIRouter(
    prefix="/api/ml",
    tags=["CU12 - Machine Learning Supervisado (Random Forest)"]
)


@router.post(
    "/predict-sales-and-premium",
    response_model=PredictionOutputDTO,
    summary="Predicción Actuarial de Prima Óptima, Riesgo y Demanda de Ventas",
    description="Calcula la prima técnica sugerida con intervalo de confianza del 95%, "
                "evalúa la propensión a siniestros y proyecta la demanda de pólizas a N meses "
                "mediante ensamble Random Forest entrenado con el histórico de Neon PostgreSQL."
)
def predict_sales_and_premium(
    payload: PredictionInputDTO,
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN"]))
) -> PredictionOutputDTO:
    """
    Ejecuta el método operacional predecirPrimaOptimaYDemanda() en el Control ICONIX.
    """
    try:
        resultado = actuarial_control.predecir_prima_optima_y_demanda(payload)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al ejecutar la inferencia actuarial: {str(e)}"
        )


@router.get(
    "/model-metrics",
    response_model=ModelMetricsDTO,
    summary="Obtener Métricas de Calidad y Feature Importances del Modelo",
    description="Retorna el R^2 Score, MAE, RMSE, exactitud de clasificación y la importancia "
                "relativa de las variables (XAI) para transparencia y auditoría actuarial."
)
def get_model_metrics(
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN"]))
) -> ModelMetricsDTO:
    """
    Ejecuta el método operacional obtenerMetricasYFeatureImportances() en el Control ICONIX.
    """
    try:
        return actuarial_control.obtener_metricas_y_feature_importances()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al recuperar métricas del modelo: {str(e)}"
        )


@router.post(
    "/retrain",
    response_model=RetrainResponseDTO,
    summary="Reentrenar Modelos Random Forest con el Dataset Histórico",
    description="Fuerza la recarga de los 1,200 registros de la tabla dataset_historico_ml_polizas "
                "en Neon PostgreSQL, ejecuta el pipeline de ajuste y actualiza los artefactos .joblib."
)
def retrain_models(
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN"]))
) -> RetrainResponseDTO:
    """
    Ejecuta el método operacional entrenarModelosRandomForest() en el Control ICONIX.
    """
    try:
        return actuarial_control.entrenar_modelos_random_forest()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el reentrenamiento de modelos: {str(e)}"
        )


@router.get(
    "/dataset-sample",
    response_model=List[Dict[str, Any]],
    summary="Obtener Muestra del Dataset Histórico para Auditoría",
    description="Retorna las primeras 10 filas del dataset histórico de Neon PostgreSQL."
)
def get_dataset_sample(
    limit: int = 10,
    current_user: CurrentUser = Depends(require_roles(["ACTUARIO", "ADMIN"]))
) -> List[Dict[str, Any]]:
    try:
        df = actuarial_control.cargar_dataset_historico()
        sample_df = df.head(min(limit, 50))
        return sample_df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar muestra del dataset: {str(e)}"
        )
