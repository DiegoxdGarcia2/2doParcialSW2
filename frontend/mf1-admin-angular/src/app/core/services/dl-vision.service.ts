/**
 * =============================================================================
 *  AegisCore AI - MF1 Angular: [CONTROL] Servicio Cliente Visión Deep Learning
 *  Caso de Uso 11 (CU11): Analizar Fotografía/Video de Siniestro con Deep Learning
 *  Metodología ICONIX - Orquestador en el Frontend
 * =============================================================================
 */

import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import {
  DamageAnalysisInput,
  DamageAssessmentOutput,
  ConfirmAssessmentResponse
} from '../models/dl-vision.models';

@Injectable({
  providedIn: 'root'
})
export class DlVisionService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'http://localhost:8000/api/dl';

  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    });
  }

  /**
   * Ejecuta el análisis de visión artificial con la CNN CrashNet
   */
  detectDamage(payload: DamageAnalysisInput): Observable<DamageAssessmentOutput> {
    return this.http.post<DamageAssessmentOutput>(
      `${this.baseUrl}/detect-damage`,
      payload,
      { headers: this.getHeaders() }
    ).pipe(
      catchError(err => {
        console.error('[DlVisionService] Error al analizar daño con CrashNet:', err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Recupera el expediente pericial de daños desde MongoDB Atlas
   */
  getClaimDamages(reclamoId: string): Observable<DamageAssessmentOutput> {
    return this.http.get<DamageAssessmentOutput>(
      `${this.baseUrl}/claim-damages/${encodeURIComponent(reclamoId)}`,
      { headers: this.getHeaders() }
    ).pipe(
      catchError(err => {
        console.error(`[DlVisionService] Error al obtener peritaje para ${reclamoId}:`, err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Confirma formalmente el peritaje y transiciona a liquidación Saga
   */
  confirmAssessment(reclamoId: string): Observable<ConfirmAssessmentResponse> {
    return this.http.post<ConfirmAssessmentResponse>(
      `${this.baseUrl}/confirm-assessment/${encodeURIComponent(reclamoId)}`,
      {},
      { headers: this.getHeaders() }
    ).pipe(
      catchError(err => {
        console.error(`[DlVisionService] Error al confirmar peritaje para ${reclamoId}:`, err);
        return throwError(() => err);
      })
    );
  }
}
