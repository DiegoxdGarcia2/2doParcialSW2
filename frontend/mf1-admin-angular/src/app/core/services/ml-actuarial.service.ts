/**
 * =============================================================================
 *  AegisCore AI - MF1 Angular: [CONTROL] Servicio Cliente Actuarial ML
 *  Metodología ICONIX - Orquestador en el Frontend
 *  Conexión a MS4 (FastAPI) con manejo de errores y tipado estricto
 * =============================================================================
 */

import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import {
  PredictionInput,
  PredictionOutput,
  ModelMetrics,
  RetrainResponse
} from '../models/ml-actuarial.models';

@Injectable({
  providedIn: 'root'
})
export class MlActuarialService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'http://localhost:8000/api/ml';

  /**
   * Genera los headers con token Keycloak SSO / Mock para desarrollo
   */
  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    });
  }

  /**
   * Inferencia actuarial de prima óptima, riesgo y demanda temporal
   */
  predictSalesAndPremium(payload: PredictionInput): Observable<PredictionOutput> {
    return this.http.post<PredictionOutput>(
      `${this.baseUrl}/predict-sales-and-premium`,
      payload,
      { headers: this.getHeaders() }
    ).pipe(
      catchError(err => {
        console.error('[MlActuarialService] Error al predecir prima y ventas:', err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Obtiene las métricas de precisión y feature importances del modelo
   */
  getModelMetrics(): Observable<ModelMetrics> {
    return this.http.get<ModelMetrics>(
      `${this.baseUrl}/model-metrics`,
      { headers: this.getHeaders() }
    ).pipe(
      catchError(err => {
        console.error('[MlActuarialService] Error al obtener métricas del modelo:', err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Solicita el reentrenamiento de los modelos contra el dataset de Neon PostgreSQL
   */
  retrainModels(): Observable<RetrainResponse> {
    return this.http.post<RetrainResponse>(
      `${this.baseUrl}/retrain`,
      {},
      { headers: this.getHeaders() }
    ).pipe(
      catchError(err => {
        console.error('[MlActuarialService] Error al reentrenar modelos:', err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Obtiene una muestra del dataset histórico para auditoría actuarial
   */
  getDatasetSample(limit: number = 10): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.baseUrl}/dataset-sample?limit=${limit}`,
      { headers: this.getHeaders() }
    ).pipe(
      catchError(err => {
        console.error('[MlActuarialService] Error al obtener muestra del dataset:', err);
        return throwError(() => err);
      })
    );
  }
}
