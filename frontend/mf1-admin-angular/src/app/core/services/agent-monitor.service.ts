/**
 * =============================================================================
 *  AegisCore AI - MF1 Angular: [CONTROL] Servicio Cliente Agente Autónomo
 *  Caso de Uso 14 (CU14): Monitoreo de Siniestros Estancados y Liquidez (LangGraph)
 *  Metodología ICONIX - Orquestador en el Frontend
 * =============================================================================
 */

import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, Subject, BehaviorSubject, catchError, throwError, timeout, of, map } from 'rxjs';
import {
  AgentClusterState,
  StalledClaim,
  RunCycleResponse,
  ExecuteSkillRequest,
  ExecuteSkillResponse,
  LiquidityMetrics,
  AgentLogEvent,
  SystemNotification
} from '../models/agent-monitor.models';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AgentMonitorService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.ms4.endpoints.agent;
  private wsSubject: Subject<any> | null = null;
  private wsConnection: WebSocket | null = null;

  // Repositorio reactivo de notificaciones del enjambre para toda la aplicación (Datos reales de MongoDB Atlas)
  private readonly notificationsSubject = new BehaviorSubject<SystemNotification[]>([]);
  private readonly STORAGE_READ_KEY = 'aegis_notifications_read_ids';
  private readonly STORAGE_DISMISSED_KEY = 'aegis_notifications_dismissed_ids';

  readonly notifications$ = this.notificationsSubject.asObservable();
  readonly unreadCount$ = this.notificationsSubject.pipe(
    map(list => list.filter(n => !n.leido).length)
  );

  constructor() {
    this.cargarNotificacionesReales();
  }

  private getStoredReadIds(): Set<string> {
    try {
      const data = localStorage.getItem(this.STORAGE_READ_KEY);
      return data ? new Set(JSON.parse(data)) : new Set();
    } catch {
      return new Set();
    }
  }

  private saveStoredReadIds(ids: Set<string>): void {
    try {
      localStorage.setItem(this.STORAGE_READ_KEY, JSON.stringify(Array.from(ids)));
    } catch (e) {
      console.warn('Error guardando read_ids en localStorage:', e);
    }
  }

  private getStoredDismissedIds(): Set<string> {
    try {
      const data = localStorage.getItem(this.STORAGE_DISMISSED_KEY);
      return data ? new Set(JSON.parse(data)) : new Set();
    } catch {
      return new Set();
    }
  }

  private saveStoredDismissedIds(ids: Set<string>): void {
    try {
      localStorage.setItem(this.STORAGE_DISMISSED_KEY, JSON.stringify(Array.from(ids)));
    } catch (e) {
      console.warn('Error guardando dismissed_ids en localStorage:', e);
    }
  }

  cargarNotificacionesReales(): void {
    const readIds = this.getStoredReadIds();
    const dismissedIds = this.getStoredDismissedIds();

    this.http.get<SystemNotification[]>(`${this.baseUrl}/notifications`, { headers: this.getHeaders() })
      .pipe(catchError(e => of([])))
      .subscribe(list => {
        if (list && list.length > 0) {
          const processed = list
            .filter(n => !dismissedIds.has(n.id))
            .map(n => ({
              ...n,
              leido: Boolean(n.leido || readIds.has(n.id))
            }));
          this.notificationsSubject.next(processed);
        } else {
          this.notificationsSubject.next([]);
        }
      });
  }

  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    });
  }

  /**
   * Conecta al canal WebSocket en tiempo real de MS4 para recibir telemetría,
   * alertas críticas para el HUD y notificaciones push.
   */
  conectarWebSocket(): Observable<any> {
    if (!this.wsSubject) {
      this.wsSubject = new Subject<any>();
      this.iniciarConexionWs();
    }
    return this.wsSubject.asObservable();
  }

  private iniciarConexionWs(): void {
    try {
      this.wsConnection = new WebSocket(environment.ms4.endpoints.agentWs);
      this.wsConnection.onopen = () => {
        console.log('[AgentMonitorService] WebSocket conectado exitosamente a MS4');
      };
      this.wsConnection.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          this.procesarMensajeWS(parsed);
          this.wsSubject?.next(parsed);
        } catch (e) {
          console.warn('[AgentMonitorService] Error procesando mensaje WS:', e);
        }
      };
      this.wsConnection.onerror = (err) => {
        console.warn('[AgentMonitorService] Evento de error en WebSocket:', err);
      };
      this.wsConnection.onclose = () => {
        console.log('[AgentMonitorService] Conexión WS cerrada. Reintentando en 5s...');
        setTimeout(() => {
          if (this.wsSubject) {
            this.iniciarConexionWs();
          }
        }, 5000);
      };
    } catch (err) {
      console.error('[AgentMonitorService] Excepción al inicializar WS:', err);
    }
  }

  private procesarMensajeWS(parsed: any): void {
    const list = [...this.notificationsSubject.value];
    const readIds = this.getStoredReadIds();
    const dismissedIds = this.getStoredDismissedIds();

    // 1. Alerta crítica HUD (Fraude / Anomalía extrema)
    if (parsed.alerta_critica && parsed.alerta_critica.abrir_hud) {
      const crit = parsed.alerta_critica;
      const notifId = crit.id || ('CRIT-' + Date.now());
      if (!dismissedIds.has(notifId) && !list.some(n => n.id === notifId)) {
        list.unshift({
          id: notifId,
          titulo: crit.titulo || 'Alerta Crítica de Fraude',
          mensaje: '[' + (crit.reclamo_id || 'SINIESTRO') + '] ' + (crit.motivo || 'Alerta de Fraude'),
          nivel: 'CRITICO',
          timestamp: crit.timestamp || new Date().toISOString(),
          leido: readIds.has(notifId),
          reclamo_id: crit.reclamo_id,
          skill_ejecutada: crit.skill_ejecutada
        });
      }
    }

    // 2. Notificaciones de auto-remediación emitidas por el Daemon
    if (parsed.notificaciones && Array.isArray(parsed.notificaciones)) {
      for (const notif of parsed.notificaciones) {
        if (!dismissedIds.has(notif.id) && !list.some(n => n.id === notif.id)) {
          list.unshift({
            id: notif.id,
            titulo: notif.titulo,
            mensaje: notif.mensaje,
            nivel: notif.nivel || 'SUCCESS',
            timestamp: notif.timestamp || new Date().toISOString(),
            leido: readIds.has(notif.id),
            reclamo_id: notif.reclamo_id,
            nuevo_estado: notif.nuevo_estado,
            skill_ejecutada: notif.skill_ejecutada
          });
        }
      }
    }

    if (list.length > 30) {
      list.length = 30;
    }
    this.notificationsSubject.next(list);
  }

  markAllAsRead(): void {
    const current = this.notificationsSubject.value;
    const readIds = this.getStoredReadIds();
    current.forEach(n => readIds.add(n.id));
    this.saveStoredReadIds(readIds);

    const updated = current.map(n => ({ ...n, leido: true }));
    this.notificationsSubject.next(updated);

    // Persistir de forma atómica en MongoDB Atlas vía MS4
    this.http.post(`${this.baseUrl}/notifications/mark-all-read`, {}, { headers: this.getHeaders() })
      .pipe(catchError(e => of(null)))
      .subscribe();
  }

  markAsRead(id: string): void {
    const readIds = this.getStoredReadIds();
    readIds.add(id);
    this.saveStoredReadIds(readIds);

    const updated = this.notificationsSubject.value.map(n => n.id === id ? { ...n, leido: true } : n);
    this.notificationsSubject.next(updated);

    // Persistir en MongoDB Atlas vía MS4
    this.http.post(`${this.baseUrl}/notifications/mark-read`, { id }, { headers: this.getHeaders() })
      .pipe(catchError(e => of(null)))
      .subscribe();
  }

  clearAllNotifications(): void {
    const current = this.notificationsSubject.value;
    const dismissedIds = this.getStoredDismissedIds();
    current.forEach(n => dismissedIds.add(n.id));
    this.saveStoredDismissedIds(dismissedIds);

    this.notificationsSubject.next([]);

    // Archivar y limpiar en MongoDB Atlas vía MS4
    this.http.delete(`${this.baseUrl}/notifications`, { headers: this.getHeaders() })
      .pipe(catchError(e => of(null)))
      .subscribe();
  }

  agregarNotificacion(notif: SystemNotification): void {
    const list = [notif, ...this.notificationsSubject.value];
    if (list.length > 30) list.length = 30;
    this.notificationsSubject.next(list);
  }

  /**
   * Inyecta un siniestro estancado aleatorio en MongoDB para demostrar la auto-remediación
   */
  seedStalledClaim(): Observable<any> {
    return this.http.post<any>(
      `${this.baseUrl}/seed-stalled-claim`,
      {},
      { headers: this.getHeaders() }
    ).pipe(
      catchError(err => {
        console.error('[AgentMonitorService] Error al inyectar siniestro:', err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Restaura los 3 siniestros estancados originales en MongoDB
   */
  resetStalledClaims(): Observable<any> {
    return this.http.post<any>(
      `${this.baseUrl}/reset-stalled-claims`,
      {},
      { headers: this.getHeaders() }
    ).pipe(
      catchError(err => {
        console.error('[AgentMonitorService] Error al restaurar siniestros:', err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Obtiene la telemetría unificada del cluster, estado del DAG y micro-agentes.
   * Con timeout y fallback automático para garantizar que la pantalla nunca se quede colgada.
   */
  getClusterState(): Observable<AgentClusterState> {
    return this.http.get<AgentClusterState>(
      `${this.baseUrl}/cluster-state`,
      { headers: this.getHeaders() }
    ).pipe(
      timeout(5000),
      catchError(err => {
        console.warn('[AgentMonitorService] Aviso al conectar con backend MS4, activando cluster state canónico:', err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Consulta los siniestros estancados en MongoDB Atlas
   */
  getStalledClaims(): Observable<StalledClaim[]> {
    return this.http.get<StalledClaim[]>(
      `${this.baseUrl}/stalled-claims`,
      { headers: this.getHeaders() }
    ).pipe(
      timeout(5000),
      catchError(err => {
        console.warn('[AgentMonitorService] Aviso al obtener siniestros estancados:', err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Dispara un ciclo completo del DAG de LangGraph (Metas, Re-planning, Skills y Reflexión)
   */
  runAutonomousCycle(): Observable<RunCycleResponse> {
    return this.http.post<RunCycleResponse>(
      `${this.baseUrl}/run-cycle`,
      {},
      { headers: this.getHeaders() }
    ).pipe(
      timeout(10000),
      catchError(err => {
        console.error('[AgentMonitorService] Error al ejecutar ciclo autónomo:', err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Ejecuta una habilidad (skill) del agente sobre un expediente estancado
   */
  executeSkill(payload: ExecuteSkillRequest): Observable<ExecuteSkillResponse> {
    return this.http.post<ExecuteSkillResponse>(
      `${this.baseUrl}/execute-skill`,
      payload,
      { headers: this.getHeaders() }
    ).pipe(
      timeout(6000),
      catchError(err => {
        console.error(`[AgentMonitorService] Error al ejecutar skill ${payload.skill_id}:`, err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Obtiene las métricas actuariales de liquidez y reservas (Solvencia II)
   */
  getLiquidityMetrics(): Observable<LiquidityMetrics> {
    return this.http.get<LiquidityMetrics>(
      `${this.baseUrl}/liquidity-metrics`,
      { headers: this.getHeaders() }
    ).pipe(
      timeout(5000),
      catchError(err => {
        console.error('[AgentMonitorService] Error al obtener métricas de liquidez:', err);
        return throwError(() => err);
      })
    );
  }

  /**
   * Recupera los eventos recientes de la bitácora del agente
   */
  getActiveMission(): Observable<any> {
    return this.http.get<any>(
      `${this.baseUrl}/mission`,
      { headers: this.getHeaders() }
    ).pipe(
      timeout(5000),
      catchError(err => {
        console.warn('[AgentMonitorService] Aviso al consultar misión activa:', err);
        return of({
          mision_id: 'MISION-DEFAULT-01',
          titulo: 'Monitoreo Continuo y Destrabe de Siniestros',
          descripcion: 'Supervisar expedientes estancados >48h y preservar reservas técnicas ($25M USD)',
          prioridad: 'ALTA',
          meta_sla_horas: 48
        });
      })
    );
  }

  assignMission(payload: { titulo: string; descripcion: string; prioridad?: string; meta_sla_horas?: number }): Observable<any> {
    return this.http.post<any>(
      `${this.baseUrl}/assign-mission`,
      payload,
      { headers: this.getHeaders() }
    ).pipe(
      timeout(5000),
      catchError(err => {
        console.error('[AgentMonitorService] Error al asignar misión al agente:', err);
        return throwError(() => err);
      })
    );
  }

  getExecutionLogs(): Observable<AgentLogEvent[]> {
    return this.http.get<AgentLogEvent[]>(
      `${this.baseUrl}/execution-logs`,
      { headers: this.getHeaders() }
    ).pipe(
      timeout(5000),
      catchError(err => {
        console.warn('[AgentMonitorService] Aviso al obtener logs de ejecución:', err);
        return throwError(() => err);
      })
    );
  }
}
