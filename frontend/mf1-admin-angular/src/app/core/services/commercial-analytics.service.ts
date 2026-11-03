/**
 * =============================================================================
 *  AegisCore AI - MF1 Angular: [CONTROL] Servicio Cliente Analítica Comercial 360°
 *  Metodología ICONIX - Orquestador Frontend para MCP + GraphQL
 *  Conecta a MS4 FastAPI para invocar tool_analitica_comercial_360
 * =============================================================================
 */

import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import {
  CommercialFilterInput,
  CommercialKpiSummary,
  FilterOptions
} from '../models/commercial-analytics.models';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class CommercialAnalyticsService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = (environment.ms4.endpoints as any).commercialAnalytics || `${environment.ms4.baseUrl}/api/commercial`;

  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    });
  }

  /**
   * Invoca la Tool MCP tool_analitica_comercial_360 pasando los filtros seleccionados
   */
  getCommercialAnalytics(filters: CommercialFilterInput): Observable<CommercialKpiSummary> {
    return this.http.post<CommercialKpiSummary>(
      `${this.baseUrl}/analytics`,
      filters,
      { headers: this.getHeaders() }
    ).pipe(
      catchError(err => {
        console.error('[CommercialAnalyticsService] Error al obtener analítica 360°:', err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Obtiene los metadatos de configuración para los selectores de la barra 360°
   */
  getFiltersMetadata(): Observable<FilterOptions> {
    return this.http.get<FilterOptions>(
      `${this.baseUrl}/filters-metadata`,
      { headers: this.getHeaders() }
    ).pipe(
      catchError(err => {
        console.error('[CommercialAnalyticsService] Error al obtener metadatos de filtros:', err);
        return throwError(() => err);
      })
    );
  }
}

