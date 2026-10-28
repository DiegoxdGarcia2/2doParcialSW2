"""
=============================================================================
 AegisCore AI - MS4: [CONTROL] Servicio Actuarial con Random Forest
 Metodología ICONIX - Clase de Control Orquestadora
 Métodos operacionales reflejados en Diagramas de Secuencia UML 2.5+
=============================================================================
"""

import os
import time
import datetime
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, accuracy_score

from app.core.config import settings
from app.db.connections import get_postgres_connection
from app.entities.ml_supervised_dto import (
    PredictionInputDTO,
    PredictionOutputDTO,
    MonthlyProjectionDTO,
    ModelMetricsDTO,
    FeatureImportanceDTO,
    RetrainResponseDTO
)


class RandomForestActuarialControl:
    """
    Clase de Control ICONIX que orquesta la carga de datos, el entrenamiento
    del ensamble Random Forest, la inferencia actuarial y las proyecciones.
    """

    NUMERIC_FEATURES = [
        "edad_asegurado",
        "antiguedad_licencia_anios",
        "anio_vehiculo",
        "valor_comercial_usd",
        "historial_siniestros_previos",
        "perfil_riesgo_score"
    ]
    CATEGORICAL_FEATURES = ["tipo_vehiculo"]

    def __init__(self):
        self.artifacts_dir = settings.ML_ARTIFACTS_DIR
        self.pipeline_premium: Optional[Pipeline] = None
        self.pipeline_claim: Optional[Pipeline] = None
        self.pipeline_sales: Optional[Pipeline] = None
        self.metrics: Optional[ModelMetricsDTO] = None
        self._ensure_models_loaded()

    def _ensure_models_loaded(self):
        """
        Carga los artefactos serializados si existen; de lo contrario, entrena
        los modelos automáticamente contra el dataset de Neon PostgreSQL.
        """
        if self._artifacts_exist():
            try:
                self.deserializar_artefactos()
                return
            except Exception as e:
                print(f"[RandomForestControl] Error cargando artefactos guardados: {e}. Reentrenando...")
        
        # Entrenamiento inicial
        try:
            self.entrenar_modelos_random_forest()
        except Exception as e:
            print(f"[RandomForestControl] Falló el entrenamiento inicial contra BD: {e}")

    def _artifacts_exist(self) -> bool:
        p1 = self.artifacts_dir / "rf_pipeline_premium.joblib"
        p2 = self.artifacts_dir / "rf_pipeline_claim.joblib"
        p3 = self.artifacts_dir / "rf_metrics.joblib"
        return p1.is_file() and p2.is_file() and p3.is_file()

    # -----------------------------------------------------------------------
    # Método Operacional UML: cargarDatasetHistorico()
    # -----------------------------------------------------------------------
    def cargar_dataset_historico(self) -> pd.DataFrame:
        """
        Extrae los 1,200 registros de la tabla dataset_historico_ml_polizas
        desde Neon PostgreSQL hacia un DataFrame de pandas.
        """
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

        # Convertir tipos numéricos explícitamente
        df["valor_comercial_usd"] = df["valor_comercial_usd"].astype(float)
        df["perfil_riesgo_score"] = df["perfil_riesgo_score"].astype(float)
        df["prima_anual_calculada"] = df["prima_anual_calculada"].astype(float)
        df["costo_siniestro_usd"] = df["costo_siniestro_usd"].astype(float)
        df["tuvo_siniestro_en_anio"] = df["tuvo_siniestro_en_anio"].astype(int)
        df["polizas_vendidas_en_mes"] = df["polizas_vendidas_en_mes"].astype(int)
        return df

    # -----------------------------------------------------------------------
    # Método Operacional UML: entrenarModelosRandomForest()
    # -----------------------------------------------------------------------
    def entrenar_modelos_random_forest(self) -> RetrainResponseDTO:
        """
        Entrena el pipeline de Scikit-Learn:
          1. Preprocesador con ColumnTransformer (OneHotEncoder + StandardScaler)
          2. RandomForestRegressor (150 estimadores) para Prima Óptima
          3. RandomForestClassifier (100 estimadores) para Probabilidad de Siniestro
          4. RandomForestRegressor (100 estimadores) para Demanda de Ventas
        """
        start_time = time.time()
        df = self.cargar_dataset_historico()

        X = df[self.NUMERIC_FEATURES + self.CATEGORICAL_FEATURES]
        y_premium = df["prima_anual_calculada"]
        y_claim = df["tuvo_siniestro_en_anio"]
        y_sales = df["polizas_vendidas_en_mes"]

        # Preprocesador
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), self.NUMERIC_FEATURES),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), self.CATEGORICAL_FEATURES)
            ]
        )

        # Split 80/20
        X_train, X_test, y_p_train, y_p_test, y_c_train, y_c_test = train_test_split(
            X, y_premium, y_claim, test_size=0.2, random_state=42
        )

        # 1. Pipeline Regresor de Primas
        regressor = RandomForestRegressor(
            n_estimators=150,
            max_depth=14,
            min_samples_split=4,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        self.pipeline_premium = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("model", regressor)
        ])
        self.pipeline_premium.fit(X_train, y_p_train)

        # Evaluación Regresor
        y_p_pred = self.pipeline_premium.predict(X_test)
        r2 = float(r2_score(y_p_test, y_p_pred))
        mae = float(mean_absolute_error(y_p_test, y_p_pred))
        rmse = float(np.sqrt(mean_squared_error(y_p_test, y_p_pred)))

        # 2. Pipeline Clasificador de Siniestralidad
        classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.pipeline_claim = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("model", classifier)
        ])
        self.pipeline_claim.fit(X_train, y_c_train)
        y_c_pred = self.pipeline_claim.predict(X_test)
        acc_claim = float(accuracy_score(y_c_test, y_c_pred))

        # 3. Pipeline Demanda de Ventas
        sales_regressor = RandomForestRegressor(
            n_estimators=100,
            max_depth=8,
            random_state=42,
            n_jobs=-1
        )
        self.pipeline_sales = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("model", sales_regressor)
        ])
        self.pipeline_sales.fit(X, y_sales)

        # Extraer Feature Importances explicables (XAI)
        rf_model: RandomForestRegressor = self.pipeline_premium.named_steps["model"]
        ohe = self.pipeline_premium.named_steps["preprocessor"].named_transformers_["cat"]
        cat_feature_names = list(ohe.get_feature_names_out(self.CATEGORICAL_FEATURES))
        all_feature_names = self.NUMERIC_FEATURES + cat_feature_names
        importances = rf_model.feature_importances_

        feature_dtos = []
        for name, imp in sorted(zip(all_feature_names, importances), key=lambda x: x[1], reverse=True):
            clean_name = name.replace("tipo_vehiculo_", "Tipo Vehículo: ").replace("_", " ").title()
            feature_dtos.append(
                FeatureImportanceDTO(
                    variable=clean_name,
                    importancia_porcentaje=round(float(imp) * 100, 2)
                )
            )

        self.metrics = ModelMetricsDTO(
            r2_score=round(r2, 4),
            mae_usd=round(mae, 2),
            rmse_usd=round(rmse, 2),
            accuracy_siniestros=round(acc_claim, 4),
            total_registros_entrenamiento=len(df),
            n_estimadores=150,
            feature_importances=feature_dtos,
            fecha_ultimo_entrenamiento=datetime.datetime.utcnow().isoformat()
        )

        # Serializar artefactos
        self.serializar_artefactos()

        elapsed = round(time.time() - start_time, 2)
        return RetrainResponseDTO(
            mensaje="Modelos Random Forest reentrenados y serializados exitosamente.",
            registros_cargados=len(df),
            r2_score_nuevo=round(r2, 4),
            mae_usd_nuevo=round(mae, 2),
            tiempo_ejecucion_segundos=elapsed,
            fecha_entrenamiento=self.metrics.fecha_ultimo_entrenamiento
        )

    # -----------------------------------------------------------------------
    # Método Operacional UML: predecirPrimaOptimaYDemanda()
    # -----------------------------------------------------------------------
    def predecir_prima_optima_y_demanda(self, payload: PredictionInputDTO) -> PredictionOutputDTO:
        """
        Ejecuta la inferencia actuarial completa:
          - Prima óptima sugerida
          - Intervalo de confianza del 95% calculando la dispersión entre árboles
          - Probabilidad de siniestro y categorización de riesgo
          - Proyección de demanda a N meses con banda de incertidumbre
        """
        if self.pipeline_premium is None or self.pipeline_claim is None:
            self.entrenar_modelos_random_forest()

        # Construir DataFrame con el registro a inferir
        input_dict = {
            "edad_asegurado": [payload.edad_asegurado],
            "antiguedad_licencia_anios": [payload.antiguedad_licencia_anios],
            "tipo_vehiculo": [payload.tipo_vehiculo.upper()],
            "anio_vehiculo": [payload.anio_vehiculo],
            "valor_comercial_usd": [payload.valor_comercial_usd],
            "historial_siniestros_previos": [payload.historial_siniestros_previos],
            "perfil_riesgo_score": [payload.perfil_riesgo_score]
        }
        df_input = pd.DataFrame(input_dict)

        # Preprocesar datos
        preprocessor = self.pipeline_premium.named_steps["preprocessor"]
        X_trans = preprocessor.transform(df_input)
        rf_regressor: RandomForestRegressor = self.pipeline_premium.named_steps["model"]

        # Inferencia por cada árbol individual del ensamble (150 árboles)
        tree_preds = np.array([tree.predict(X_trans)[0] for tree in rf_regressor.estimators_])

        mean_premium = float(np.mean(tree_preds))
        std_premium = float(np.std(tree_preds))
        conf_min = float(np.percentile(tree_preds, 5))
        conf_max = float(np.percentile(tree_preds, 95))

        # Inferencia de siniestralidad con el clasificador
        prob_claim = float(self.pipeline_claim.predict_proba(df_input)[0][1]) * 100.0

        # Categorización de riesgo
        if prob_claim < 20.0:
            nivel_riesgo = "BAJO"
            costo_estimado = payload.valor_comercial_usd * 0.08
        elif prob_claim < 40.0:
            nivel_riesgo = "MEDIO"
            costo_estimado = payload.valor_comercial_usd * 0.18
        elif prob_claim < 65.0:
            nivel_riesgo = "ALTO"
            costo_estimado = payload.valor_comercial_usd * 0.35
        else:
            nivel_riesgo = "CRÍTICO"
            costo_estimado = payload.valor_comercial_usd * 0.55

        # Proyección de ventas a N meses
        base_sales = float(self.pipeline_sales.predict(df_input)[0]) if self.pipeline_sales else 115.0
        today = datetime.date.today()
        proyecciones = []

        for m in range(1, payload.meses_a_proyectar + 1):
            future_date = today + datetime.timedelta(days=30 * m)
            month_str = future_date.strftime("%Y-%m")
            # Ajuste estacional simulado y ligero crecimiento por tendencia
            seasonal_factor = 1.0 + 0.03 * np.sin(m * np.pi / 6)
            projected_sales = int(round(base_sales * seasonal_factor + (m * 2.5)))
            projected_premium = round(mean_premium * (1.0 + (m * 0.005)), 2)
            margin = round(std_premium * 1.645, 2)  # Cota 95% aproximada

            proyecciones.append(
                MonthlyProjectionDTO(
                    mes=month_str,
                    ventas_estimadas_polizas=projected_sales,
                    prima_sugerida_usd=projected_premium,
                    intervalo_confianza_min=max(200.0, round(projected_premium - margin, 2)),
                    intervalo_confianza_max=round(projected_premium + margin, 2)
                )
            )

        return PredictionOutputDTO(
            prima_anual_optima_usd=round(mean_premium, 2),
            rango_confianza_95=[round(conf_min, 2), round(conf_max, 2)],
            desviacion_estandar_usd=round(std_premium, 2),
            probabilidad_siniestro_pct=round(prob_claim, 2),
            nivel_riesgo_clasificado=nivel_riesgo,
            costo_siniestro_estimado_usd=round(costo_estimado, 2),
            proyecciones_mensuales=proyecciones,
            metricas_modelo=self.metrics
        )

    # -----------------------------------------------------------------------
    # Método Operacional UML: obtenerMetricasYFeatureImportances()
    # -----------------------------------------------------------------------
    def obtener_metricas_y_feature_importances(self) -> ModelMetricsDTO:
        """
        Retorna las métricas y la importancia de variables del modelo actual.
        """
        if self.metrics is None:
            self.entrenar_modelos_random_forest()
        return self.metrics

    def serializar_artefactos(self):
        """Guarda pipelines y métricas a disco usando joblib."""
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.pipeline_premium, self.artifacts_dir / "rf_pipeline_premium.joblib")
        joblib.dump(self.pipeline_claim, self.artifacts_dir / "rf_pipeline_claim.joblib")
        joblib.dump(self.pipeline_sales, self.artifacts_dir / "rf_pipeline_sales.joblib")
        joblib.dump(self.metrics, self.artifacts_dir / "rf_metrics.joblib")

    def deserializar_artefactos(self):
        """Carga pipelines y métricas desde disco usando joblib."""
        self.pipeline_premium = joblib.load(self.artifacts_dir / "rf_pipeline_premium.joblib")
        self.pipeline_claim = joblib.load(self.artifacts_dir / "rf_pipeline_claim.joblib")
        self.pipeline_sales = joblib.load(self.artifacts_dir / "rf_pipeline_sales.joblib")
        self.metrics = joblib.load(self.artifacts_dir / "rf_metrics.joblib")


# Singleton para inyección de dependencias en FastAPI
actuarial_control = RandomForestActuarialControl()
