/**
 * =============================================================================
 *  AegisCore AI - MF1 Angular: [CONTROL] Servicio Cliente de Detección de Fraude ML
 *  Metodología ICONIX - Orquestador en el Frontend
 *  Conexión a MS4 (FastAPI) para K-Means e Isolation Forest (CU13)
 * =============================================================================
 */

import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import {
  FraudDashboardSummary,
  FraudAlert,
  EvaluateClaimInput,
  FreezeClaimResponse
} from '../models/ml-unsupervised.models';

@Injectable({
  providedIn: 'root'
})
export class MlUnsupervisedService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'http://localhost:8000/api/ml/unsupervised';

  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    });
  }

  /**
   * Obtiene el resumen consolidado de segmentación (K-Means) y detección de fraude (Isolation Forest)
   */
  getClustersAndAnomalies(): Observable<FraudDashboardSummary> {
    return this.http.get<FraudDashboardSummary>(
      `${this.baseUrl}/clusters-and-anomalies`,
      { headers: this.getHeaders() }
    ).pipe(
      catchError(err => {
        console.error('[MlUnsupervisedService] Error al obtener telemetría de fraude y clusters:', err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Evalúa un siniestro en tiempo real contra el Isolation Forest
   */
  evaluateClaim(payload: EvaluateClaimInput): Observable<FraudAlert> {
    return this.http.post<FraudAlert>(
      `${this.baseUrl}/evaluate-claim`,
      payload,
      { headers: this.getHeaders() }
    ).pipe(
      catchError(err => {
        console.error('[MlUnsupervisedService] Error al evaluar siniestro con Isolation Forest:', err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Congela preventivamente el pago en MongoDB Atlas (expedientes_siniestros)
   */
  freezeClaim(reclamoId: string): Observable<FreezeClaimResponse> {
    return this.http.post<FreezeClaimResponse>(
      `${this.baseUrl}/freeze-claim/${encodeURIComponent(reclamoId)}`,
      {},
      { headers: this.getHeaders() }
    ).pipe(
      catchError(err => {
        console.error(`[MlUnsupervisedService] Error al congelar reclamo ${reclamoId}:`, err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Obtiene listado de alertas de fraude vivas desde MongoDB Atlas
   */
  getAlerts(limit: number = 50): Observable<FraudAlert[]> {
    return this.http.get<FraudAlert[]>(
      `${this.baseUrl}/alerts?limit=${limit}`,
      { headers: this.getHeaders() }
    ).pipe(
      catchError(err => {
        console.error('[MlUnsupervisedService] Error al listar alertas de fraude:', err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Solicita el reentrenamiento de K-Means e Isolation Forest
   */
  retrainModels(): Observable<any> {
    return this.http.post<any>(
      `${this.baseUrl}/retrain`,
      {},
      { headers: this.getHeaders() }
    ).pipe(
      catchError(err => {
        console.error('[MlUnsupervisedService] Error al reentrenar modelos no supervisados:', err);
        return throwError(() => err);
      })
    );
  }
}
