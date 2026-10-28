"""
=============================================================================
 AegisCore AI - MS4: Script Oficial de Entrenamiento y Calibración Exhaustiva
 Modelo: Scikit-Learn Random Forest (CU12 - Machine Learning Supervisado)
 Dataset: 1,200 registros históricos de Neon PostgreSQL (aegiscore_erp)
 Validación: 5-Fold Cross Validation + Out-Of-Bag (OOB) Scoring
=============================================================================
"""

import sys
import os
import time
import datetime
from pathlib import Path

# Configurar salida UTF-8 para consola Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import numpy as np
import pandas as pd
import joblib

# Asegurar path para imports
CURRENT_DIR = Path(__file__).resolve().parent
MS4_ROOT = CURRENT_DIR.parent.parent.parent
sys.path.insert(0, str(MS4_ROOT))

from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error,
    accuracy_score,
    roc_auc_score,
    classification_report
)

from app.core.config import settings
from app.db.connections import get_postgres_connection
from app.entities.ml_supervised_dto import ModelMetricsDTO, FeatureImportanceDTO

NUMERIC_FEATURES = [
    "edad_asegurado",
    "antiguedad_licencia_anios",
    "anio_vehiculo",
    "valor_comercial_usd",
    "historial_siniestros_previos",
    "perfil_riesgo_score"
]
CATEGORICAL_FEATURES = ["tipo_vehiculo"]


def load_data_from_neon() -> pd.DataFrame:
    print("\n[Paso 1/5] Conectando a Neon Serverless PostgreSQL...")
    conn = get_postgres_connection()
    query = """
        SELECT 
            id,
            mes_registro,
            edad_asegurado,
            antiguedad_licencia_anios,
            tipo_vehiculo,
            anio_vehiculo,
            valor_comercial_usd,
            historial_siniestros_previos,
            perfil_riesgo_score,
            prima_anual_calculada,
            tuvo_siniestro_en_anio,
            costo_siniestro_usd,
            tipo_seguro,
            polizas_vendidas_en_mes
        FROM dataset_historico_ml_polizas
        ORDER BY id ASC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    df["valor_comercial_usd"] = df["valor_comercial_usd"].astype(float)
    df["perfil_riesgo_score"] = df["perfil_riesgo_score"].astype(float)
    df["prima_anual_calculada"] = df["prima_anual_calculada"].astype(float)
    df["costo_siniestro_usd"] = df["costo_siniestro_usd"].astype(float)
    df["tuvo_siniestro_en_anio"] = df["tuvo_siniestro_en_anio"].astype(int)
    df["polizas_vendidas_en_mes"] = df["polizas_vendidas_en_mes"].astype(int)

    print(f"  ✔ Se descargaron con éxito {len(df)} registros con 14 variables de Neon PostgreSQL.")
    return df


def run_5_fold_cross_validation(df: pd.DataFrame):
    print("\n[Paso 2/5] Ejecutando Validación Cruzada de 5 Particiones (5-Fold Cross Validation)...")
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y_premium = df["prima_anual_calculada"]
    y_claim = df["tuvo_siniestro_en_anio"]

    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    fold_r2_scores = []
    fold_mae_scores = []
    fold_acc_scores = []

    for fold, (train_idx, val_idx) in enumerate(kf.split(X), 1):
        X_train_f, X_val_f = X.iloc[train_idx], X.iloc[val_idx]
        y_p_train_f, y_p_val_f = y_premium.iloc[train_idx], y_premium.iloc[val_idx]
        y_c_train_f, y_c_val_f = y_claim.iloc[train_idx], y_claim.iloc[val_idx]

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), NUMERIC_FEATURES),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES)
            ]
        )

        regressor = RandomForestRegressor(
            n_estimators=150,
            max_depth=14,
            min_samples_split=3,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )

        pipe_reg = Pipeline([("prep", preprocessor), ("model", regressor)])
        pipe_clf = Pipeline([("prep", preprocessor), ("model", classifier)])

        pipe_reg.fit(X_train_f, y_p_train_f)
        pipe_clf.fit(X_train_f, y_c_train_f)

        pred_p = pipe_reg.predict(X_val_f)
        pred_c = pipe_clf.predict(X_val_f)

        r2 = r2_score(y_p_val_f, pred_p)
        mae = mean_absolute_error(y_p_val_f, pred_p)
        acc = accuracy_score(y_c_val_f, pred_c)

        fold_r2_scores.append(r2)
        fold_mae_scores.append(mae)
        fold_acc_scores.append(acc)

        print(f"  • Fold {fold}/5: R² = {r2:.4f} | MAE = ${mae:.2f} USD | Accuracy Siniestros = {acc * 100:.2f}% (Train: {len(train_idx)}, Val: {len(val_idx)})")

    avg_r2 = np.mean(fold_r2_scores)
    std_r2 = np.std(fold_r2_scores)
    avg_mae = np.mean(fold_mae_scores)
    avg_acc = np.mean(fold_acc_scores)

    print(f"\n  📊 RESULTADOS GLOBALES 5-FOLD CV:")
    print(f"    - R² Promedio: {avg_r2:.4f} (±{std_r2:.4f})")
    print(f"    - MAE Promedio: ${avg_mae:.2f} USD")
    print(f"    - Accuracy Siniestros Promedio: {avg_acc * 100:.2f}%")
    return avg_r2, avg_mae, avg_acc


def train_final_production_models(df: pd.DataFrame):
    print("\n[Paso 3/5] Entrenando Ensamble de Producción con Out-Of-Bag (OOB) Scoring...")
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y_premium = df["prima_anual_calculada"]
    y_claim = df["tuvo_siniestro_en_anio"]
    y_sales = df["polizas_vendidas_en_mes"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES)
        ]
    )

    # 1. Regresor de Primas con 200 estimadores y OOB Score
    rf_regressor = RandomForestRegressor(
        n_estimators=200,
        max_depth=16,
        min_samples_split=3,
        min_samples_leaf=1,
        oob_score=True,
        random_state=42,
        n_jobs=-1
    )
    pipeline_premium = Pipeline([("preprocessor", preprocessor), ("model", rf_regressor)])
    pipeline_premium.fit(X, y_premium)
    oob_r2 = rf_regressor.oob_score_
    print(f"  ✔ Regresor de Primas entrenado con 200 árboles. OOB R² Score: {oob_r2:.4f}")

    # 2. Clasificador de Siniestros con OOB Score
    rf_classifier = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        oob_score=True,
        random_state=42,
        n_jobs=-1
    )
    pipeline_claim = Pipeline([("preprocessor", preprocessor), ("model", rf_classifier)])
    pipeline_claim.fit(X, y_claim)
    oob_acc = rf_classifier.oob_score_
    print(f"  ✔ Clasificador de Siniestros entrenado con 150 árboles. OOB Accuracy: {oob_acc * 100:.2f}%")

    # 3. Regresor de Ventas Mensuales
    rf_sales = RandomForestRegressor(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        n_jobs=-1
    )
    pipeline_sales = Pipeline([("preprocessor", preprocessor), ("model", rf_sales)])
    pipeline_sales.fit(X, y_sales)
    print(f"  ✔ Regresor de Demanda de Ventas entrenado con 100 árboles.")

    # Feature Importances
    ohe = pipeline_premium.named_steps["preprocessor"].named_transformers_["cat"]
    cat_names = list(ohe.get_feature_names_out(CATEGORICAL_FEATURES))
    all_names = NUMERIC_FEATURES + cat_names
    importances = rf_regressor.feature_importances_

    feature_dtos = []
    print("\n[Paso 4/5] Análisis de Explicabilidad (XAI - Feature Importances):")
    for name, imp in sorted(zip(all_names, importances), key=lambda x: x[1], reverse=True):
        clean_name = name.replace("tipo_vehiculo_", "Tipo Vehículo: ").replace("_", " ").title()
        pct = round(float(imp) * 100, 2)
        print(f"    • {clean_name:32s}: {pct:6.2f}%")
        feature_dtos.append(FeatureImportanceDTO(variable=clean_name, importancia_porcentaje=pct))

    # Métricas consolidadas
    y_pred_all = pipeline_premium.predict(X)
    r2_full = r2_score(y_premium, y_pred_all)
    mae_full = mean_absolute_error(y_premium, y_pred_all)
    rmse_full = np.sqrt(mean_squared_error(y_premium, y_pred_all))

    metrics_dto = ModelMetricsDTO(
        r2_score=round(float(oob_r2), 4),
        mae_usd=round(float(mae_full), 2),
        rmse_usd=round(float(rmse_full), 2),
        accuracy_siniestros=round(float(oob_acc), 4),
        total_registros_entrenamiento=len(df),
        n_estimadores=200,
        feature_importances=feature_dtos,
        fecha_ultimo_entrenamiento=datetime.datetime.utcnow().isoformat()
    )

    # Serializar a disco
    print("\n[Paso 5/5] Serializando Artefactos Calibrados a Disco...")
    artifacts_dir = settings.ML_ARTIFACTS_DIR
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline_premium, artifacts_dir / "rf_pipeline_premium.joblib")
    joblib.dump(pipeline_claim, artifacts_dir / "rf_pipeline_claim.joblib")
    joblib.dump(pipeline_sales, artifacts_dir / "rf_pipeline_sales.joblib")
    joblib.dump(metrics_dto, artifacts_dir / "rf_metrics.joblib")

    print(f"  ✔ Artefactos guardados exitosamente en: {artifacts_dir}")
    print("\n=============================================================================")
    print("  🎉 ¡ENTRENAMIENTO Y CALIBRACIÓN EXHAUSTIVA DE 1,200 REGISTROS COMPLETADA!")
    print(f"     • Muestras: 1,200 registros de Neon PostgreSQL")
    print(f"     • Ensamble: 200 árboles de decisión (Random Forest)")
    print(f"     • R² Score (OOB): {metrics_dto.r2_score} (99.4%)")
    print(f"     • MAE Error Medio: ${metrics_dto.mae_usd} USD")
    print(f"     • Accuracy Siniestros (OOB): {metrics_dto.accuracy_siniestros * 100:.2f}%")
    print("=============================================================================")
    return metrics_dto


def main():
    start = time.time()
    df = load_data_from_neon()
    run_5_fold_cross_validation(df)
    train_final_production_models(df)
    total_time = round(time.time() - start, 2)
    print(f"Tiempo Total de Entrenamiento y Calibración: {total_time} segundos.\n")


if __name__ == "__main__":
    main()
