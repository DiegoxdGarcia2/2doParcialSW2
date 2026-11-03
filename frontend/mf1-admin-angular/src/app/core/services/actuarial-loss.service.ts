/**
 * =============================================================================
 *  AegisCore AI - MF1 Angular: [CONTROL] Servicio Cliente Siniestralidad Real 360°
 *  Metodología ICONIX - Orquestador Frontend para Siniestralidad y Riesgo Demográfico
 *  Consume endpoints FastAPI que ejecutan consultas SQL 100% puras en PostgreSQL
 * =============================================================================
 */

import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import {
  ActuarialLossFilterInput,
  ActuarialLossSummary,
  ActuarialFilterOptions
} from '../models/actuarial-loss.models';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ActuarialLossService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = (environment.ms4.endpoints as any).actuarialLoss || `${environment.ms4.baseUrl}/api/actuarial/loss`;

  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    });
  }

  /**
   * Invoca la analítica de siniestralidad real ejecutada en PostgreSQL
   */
  getLossAnalytics(filters: ActuarialLossFilterInput): Observable<ActuarialLossSummary> {
    return this.http.post<ActuarialLossSummary>(
      `${this.baseUrl}/analytics`,
      filters,
      { headers: this.getHeaders() }
    ).pipe(
      catchError(err => {
        console.error('[ActuarialLossService] Error al obtener analítica de siniestralidad:', err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Obtiene los metadatos de configuración para los selectores de la barra de filtros
   */
  getLossFiltersMetadata(): Observable<ActuarialFilterOptions> {
    return this.http.get<ActuarialFilterOptions>(
      `${this.baseUrl}/filters-metadata`,
      { headers: this.getHeaders() }
    ).pipe(
      catchError(err => {
        console.error('[ActuarialLossService] Error al obtener metadatos de filtros actuariales:', err);
        return throwError(() => err);
      })
    );
  }
}

