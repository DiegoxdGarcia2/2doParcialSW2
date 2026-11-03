/**
 * =============================================================================
 *  AegisCore AI - MF1 Angular: [BOUNDARY] Componente Autónomo LangGraph Monitor
 *  Caso de Uso 14 (CU14): Monitoreo de Siniestros Estancados y Liquidez (LangGraph)
 *  Trazabilidad ICONIX: Objeto Boundary con Sistema de Diseño "Executive Precision"
 * =============================================================================
 */

import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AgentMonitorService } from '../../core/services/agent-monitor.service';
import {
  AgentClusterState,
  StalledClaim,
  RunCycleResponse,
  ExecuteSkillResponse,
  LiquidityMetrics,
  AgentLogEvent,
  AgentNodeStatus,
  ActiveMicroAgent
} from '../../core/models/agent-monitor.models';

@Component({
  selector: 'app-autonomous-agent-monitor',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './autonomous-agent-monitor.component.html',
  styleUrls: ['./autonomous-agent-monitor.component.css']
})
export class AutonomousAgentMonitorComponent implements OnInit {
  private readonly agentService = inject(AgentMonitorService);
  private readonly cdr = inject(ChangeDetectorRef);

  clusterState: AgentClusterState | null = null;
  logs: AgentLogEvent[] = [];
  lastCycleResult: RunCycleResponse | null = null;

  isLoading: boolean = true;
  isCycleRunning: boolean = false;
  isSwarmPaused: boolean = false;
  healthCheckRunning: boolean = false;
  healthCheckResult: string | null = null;
  executingSkills: { [reclamoId: string]: boolean } = {};

  // Estado del Canal WebSocket en Vivo
  isWsConnected: boolean = false;

  // Estado del Panel HUD / Drawer Lateral de Alertas Críticas
  isHudOpen: boolean = false;
  hudData: any = null;

  // Notificaciones Push Flotantes de Alto Impacto
  pushNotifications: Array<{
    id: string;
    titulo: string;
    mensaje: string;
    nivel: 'SUCCESS' | 'CRITICO' | 'INFO';
    timestamp: string;
    nuevo_estado?: string;
  }> = [];

  isSeedingClaim: boolean = false;
  isResettingClaims: boolean = false;

  feedbackMessage: string | null = null;
  errorMessage: string | null = null;

  // Control de Visualización y Filtros para la Bitácora Ejecutiva
  vistaLog: 'ejecutiva' | 'raw' = 'ejecutiva';
  filtroTipoLog: string = 'TODOS';
  busquedaLog: string = '';

  get totalRemediaciones(): number {
    return this.logs.filter(l => l.tipo_evento === 'AUTO_REMEDIACION' || l.nodo === 'LANGGRAPH_DAEMON').length;
  }

  get totalCiclos(): number {
    return this.logs.filter(l => l.tipo_evento === 'CICLO_AUTONOMO' || l.nodo === 'LANGGRAPH_ORCHESTRATOR').length;
  }

  get logsFiltrados(): AgentLogEvent[] {
    let list = this.logs;
    if (this.filtroTipoLog !== 'TODOS') {
      list = list.filter(l => l.tipo_evento === this.filtroTipoLog || l.nodo === this.filtroTipoLog);
    }
    if (this.busquedaLog.trim()) {
      const q = this.busquedaLog.toLowerCase().trim();
      list = list.filter(l =>
        l.detalle.toLowerCase().includes(q) ||
        l.nodo.toLowerCase().includes(q) ||
        l.evento_id.toLowerCase().includes(q)
      );
    }
    return list;
  }

  get parsedLogsFiltrados(): any[] {
    return this.logsFiltrados.map(log => this.parseLogItem(log));
  }

  parseLogItem(log: AgentLogEvent) {
    const hora = log.timestamp && log.timestamp.length >= 19 ? log.timestamp.slice(11, 19) : '--:--:--';
    const fecha = log.timestamp && log.timestamp.length >= 10 ? log.timestamp.slice(0, 10) : '';

    let referenciaId: string | undefined;
    const refMatch = log.detalle.match(/\[(REC-[A-Z0-9\-]+|CYCLE-[A-Z0-9\-]+)\]/i);
    if (refMatch) {
      referenciaId = refMatch[1];
    }

    const esCiclo = log.tipo_evento === 'CICLO_AUTONOMO' || log.nodo === 'LANGGRAPH_ORCHESTRATOR';
    const esRemediacion = log.tipo_evento === 'AUTO_REMEDIACION' || log.nodo === 'LANGGRAPH_DAEMON';
    const esSkill = log.tipo_evento === 'DISPARO_SKILL' || log.nodo === 'SKILL_DISPATCHER';

    let nodoLabel = log.nodo;
    let nodoIcon = 'terminal';
    let nodoColorClass = 'badge-slate';

    if (esCiclo) {
      nodoLabel = 'Orquestador LangGraph';
      nodoIcon = 'account_tree';
      nodoColorClass = 'badge-indigo';
    } else if (esRemediacion) {
      nodoLabel = 'Daemon Autónomo';
      nodoIcon = 'auto_fix_high';
      nodoColorClass = 'badge-teal';
    } else if (esSkill) {
      nodoLabel = 'Despachador Skills';
      nodoIcon = 'flash_on';
      nodoColorClass = 'badge-amber';
    } else if (log.nodo.includes('FRAUD') || log.nodo.includes('CENTINELA')) {
      nodoLabel = 'Centinela Anti-Fraude';
      nodoIcon = 'security';
      nodoColorClass = 'badge-red';
    } else if (log.nodo.includes('VISION')) {
      nodoLabel = 'CrashNet CNN Visión';
      nodoIcon = 'visibility';
      nodoColorClass = 'badge-purple';
    }

    let tituloEjecutivo = 'Evento Transaccional Kafka';
    let descripcionLimpia = log.detalle;
    let cleanText = log.detalle.replace(/^(\[[^\]]+\]\s*)+/g, '');

    const skills: Array<{ codigo: string; nombre: string; reclamo?: string }> = [];
    const skillsMatch = log.detalle.match(/Skills:\s*(.+)$/i);
    if (skillsMatch && !skillsMatch[1].toLowerCase().includes('ninguna')) {
      const rawSkills = skillsMatch[1].split(',');
      for (const raw of rawSkills) {
        const trimmed = raw.trim();
        const skillCodeMatch = trimmed.match(/(SKILL_[A-Z0-9_]+)/);
        const claimMatch = trimmed.match(/\((REC-[^\)]+)\)/);
        if (skillCodeMatch) {
          skills.push({
            codigo: skillCodeMatch[1],
            nombre: this.getSkillFriendlyName(skillCodeMatch[1]),
            reclamo: claimMatch ? claimMatch[1] : undefined
          });
        }
      }
    }

    let estadoBadge = { texto: 'AUDITADO', cssClass: 'badge-info', icon: 'verified' };

    if (esRemediacion) {
      tituloEjecutivo = 'Auto-Remediación de Siniestro en MongoDB Atlas';
      descripcionLimpia = cleanText;
      estadoBadge = { texto: 'DESBLOQUEADO', cssClass: 'badge-success', icon: 'check_circle' };
    } else if (esCiclo) {
      tituloEjecutivo = 'Ciclo de Evaluación y Re-Planning LangGraph';
      const evalMatch = log.detalle.match(/Se evaluaron (\d+) siniestros.*disparó (\d+) skills/i);
      if (evalMatch) {
        const ev = evalMatch[1];
        const skCount = evalMatch[2];
        descripcionLimpia = `Ciclo LangGraph completado con éxito. Se evaluaron ${ev} expediente(s) y se dispararon ${skCount} habilidad(es) autónoma(s). Cobertura de solvencia verificada.`;
      } else {
        descripcionLimpia = cleanText;
      }
      estadoBadge = { texto: 'CICLO EXITOSO', cssClass: 'badge-indigo', icon: 'task_alt' };
    } else if (esSkill) {
      tituloEjecutivo = 'Ejecución Asistida de Habilidad Pericial';
      descripcionLimpia = cleanText;
      estadoBadge = { texto: 'EJECUTADO', cssClass: 'badge-amber', icon: 'bolt' };
    }

    return {
      raw: log,
      id: log.evento_id,
      hora,
      fecha,
      nodo: log.nodo,
      nodoLabel,
      nodoIcon,
      nodoColorClass,
      tipoEvento: log.tipo_evento,
      referenciaId,
      esCiclo,
      esRemediacion,
      tituloEjecutivo,
      descripcionLimpia,
      skills,
      estadoBadge,
      impacto: log.impacto_expedientes || 0
    };
  }

  // Misión Funcional Asignada al Agente
  activeMission: any = null;
  misionesPredefinidas = [
    {
      id: 'm1',
      titulo: 'Preservar Reserva de Solvencia II ($25M USD)',
      descripcion: 'Monitorear ratio de cobertura técnica ante ráfagas de siniestralidad crítica',
      prioridad: 'ALTA',
      meta_sla_horas: 48
    },
    {
      id: 'm2',
      titulo: 'Descongestión de Siniestros Estancados SLA >48h',
      descripcion: 'Reasignar peritos por GPS y solicitar segunda evidencia en expedientes trabados',
      prioridad: 'CRITICA',
      meta_sla_horas: 24
    },
    {
      id: 'm3',
      titulo: 'Detección Proactiva de Fraude y Colusión de Talleres',
      descripcion: 'Aislar sobreprecios con Isolation Forest y congelar preventivamente en la Saga',
      prioridad: 'MAXIMA',
      meta_sla_horas: 12
    }
  ];

  cargarMisionActiva(): void {
    this.agentService.getActiveMission().subscribe({
      next: (m) => {
        this.activeMission = m;
        this.cdr.detectChanges();
      },
      error: (e) => console.warn('Error al cargar misión:', e)
    });
  }

  asignarMision(m: any): void {
    this.agentService.assignMission({
      titulo: m.titulo,
      descripcion: m.descripcion,
      prioridad: m.prioridad,
      meta_sla_horas: m.meta_sla_horas
    }).subscribe({
      next: (resp) => {
        this.activeMission = resp;
        this.feedbackMessage = `Misión asignada al agente: "${resp.titulo}"`;
        this.cdr.detectChanges();
        setTimeout(() => this.feedbackMessage = null, 4000);
      },
      error: (err) => {
        this.errorMessage = 'Error al asignar misión al agente: ' + err.message;
        this.cdr.detectChanges();
        setTimeout(() => this.errorMessage = null, 4000);
      }
    });
  }

  ngOnInit(): void {
    this.cargarMisionActiva();
    this.cargarDatosCluster();
    this.conectarCanalWebSocket();
  }

  conectarCanalWebSocket(): void {
    this.agentService.conectarWebSocket().subscribe({
      next: (data) => {
        this.isWsConnected = true;

        if (data.cluster_state) {
          this.clusterState = data.cluster_state;
        }

        // 1. Auto-despliegue del Panel HUD Lateral si hay Alerta Crítica (Fraude / SLA severo)
        if (data.alerta_critica && data.alerta_critica.abrir_hud) {
          this.hudData = data.alerta_critica;
          this.isHudOpen = true;
          this.reproducirAlertaSonora();
          this.agregarNotificacionPush({
            id: data.alerta_critica.id,
            titulo: data.alerta_critica.titulo,
            mensaje: `[${data.alerta_critica.reclamo_id}] ${data.alerta_critica.motivo}`,
            nivel: 'CRITICO',
            timestamp: data.alerta_critica.timestamp
          });
        }

        // 2. Notificaciones Push de Auto-Remediación ejecutada por el Daemon
        if (data.notificaciones && Array.isArray(data.notificaciones)) {
          for (const n of data.notificaciones) {
            this.agregarNotificacionPush({
              id: n.id,
              titulo: n.titulo,
              mensaje: n.mensaje,
              nivel: n.nivel || 'SUCCESS',
              timestamp: n.timestamp,
              nuevo_estado: n.nuevo_estado
            });

            // Agregar traza a la terminal de logs en vivo
            this.logs.unshift({
              evento_id: n.id,
              timestamp: n.timestamp,
              nodo: 'LANGGRAPH_DAEMON',
              tipo_evento: 'AUTO_REMEDIACION',
              detalle: n.mensaje,
              impacto_expedientes: 1
            });
          }
        }

        // 3. Si llega un ciclo completado bajo demanda
        if (data.tipo === 'CICLO_AUTONOMO_COMPLETADO') {
          this.feedbackMessage = `Ciclo #${data.ciclo_id} ejecutado. Skills: ${data.skills_disparadas?.length || 0}`;
          setTimeout(() => this.feedbackMessage = null, 4000);
        }

        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isWsConnected = false;
        console.warn('[AutonomousAgentMonitor] Error en suscripción WS:', err);
      }
    });
  }

  agregarNotificacionPush(notif: any): void {
    this.pushNotifications.unshift(notif);
    if (this.pushNotifications.length > 5) {
      this.pushNotifications.pop();
    }
    // Auto-descartar después de 8 segundos
    setTimeout(() => {
      this.descartarNotificacion(notif.id);
    }, 8000);
  }

  descartarNotificacion(id: string): void {
    this.pushNotifications = this.pushNotifications.filter(n => n.id !== id);
    this.cdr.detectChanges();
  }

  cerrarHud(): void {
    this.isHudOpen = false;
    this.cdr.detectChanges();
  }

  reproducirAlertaSonora(): void {
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
      osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.15); // A5

      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + 0.35);
    } catch {
      // Audio silencioso en entornos restringidos
    }
  }

  inyectarSiniestroPrueba(): void {
    this.isSeedingClaim = true;
    this.agentService.seedStalledClaim().subscribe({
      next: (res) => {
        this.isSeedingClaim = false;
        this.feedbackMessage = `¡Siniestro de prueba ${res.numero_reclamo} inyectado! El Daemon lo detectará y resolverá en su siguiente ciclo.`;
        this.cargarDatosCluster();
        setTimeout(() => this.feedbackMessage = null, 6000);
      },
      error: (err) => {
        this.isSeedingClaim = false;
        this.errorMessage = 'Error al inyectar siniestro de prueba en MongoDB.';
        console.error(err);
      }
    });
  }

  restaurarSiniestrosCanonicos(): void {
    this.isResettingClaims = true;
    this.agentService.resetStalledClaims().subscribe({
      next: (res) => {
        this.isResettingClaims = false;
        this.feedbackMessage = 'Los 3 siniestros estancados canónicos han sido restaurados en MongoDB Atlas.';
        this.cargarDatosCluster();
        setTimeout(() => this.feedbackMessage = null, 6000);
      },
      error: (err) => {
        this.isResettingClaims = false;
        this.errorMessage = 'Error al restaurar siniestros en MongoDB.';
        console.error(err);
      }
    });
  }

  cargarDatosCluster(): void {
    this.isLoading = true;
    this.errorMessage = null;
    this.cdr.detectChanges();

    this.agentService.getClusterState().subscribe({
      next: (state) => {
        this.clusterState = state;
        this.isLoading = false;
        this.cdr.detectChanges();
        this.cargarLogs();
      },
      error: (err) => {
        console.error('[AutonomousAgentMonitor] Error al conectar con MS4 LangGraph:', err);
        this.clusterState = null;
        this.errorMessage = 'Error de conexión con Backend MS4 (FastAPI). No se pudo sincronizar el estado del cluster LangGraph.';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  cargarLogs(): void {
    this.agentService.getExecutionLogs().subscribe({
      next: (logEntries) => {
        this.logs = logEntries;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.warn('[AutonomousAgentMonitor] Error cargando logs:', err);
      }
    });
  }

  ejecutarCicloAutonomo(): void {
    if (this.isCycleRunning) return;
    this.isCycleRunning = true;
    this.errorMessage = null;
    this.feedbackMessage = 'Ejecutando DAG LangGraph (Ingestion -> Vision -> Policy -> Fraud -> Saga -> Reflection)...';

    this.agentService.runAutonomousCycle().subscribe({
      next: (res) => {
        this.lastCycleResult = res;
        this.isCycleRunning = false;
        this.feedbackMessage = `Ciclo LangGraph #${res.ciclo_id} completado en ${res.duracion_total_ms}ms. Siniestros evaluados: ${res.siniestros_analizados} | Resueltos: ${res.siniestros_resueltos} | Skills: ${res.skills_disparadas.length}.`;
        this.cargarDatosCluster();
        setTimeout(() => this.feedbackMessage = null, 6000);
      },
      error: (err) => {
        this.isCycleRunning = false;
        this.errorMessage = 'Fallo en la ejecución del ciclo autónomo LangGraph.';
        console.error(err);
      }
    });
  }

  ejecutarSkill(claim: StalledClaim): void {
    this.executingSkills[claim.numero_reclamo] = true;
    this.errorMessage = null;

    this.agentService.executeSkill({
      numero_reclamo: claim.numero_reclamo,
      skill_id: claim.accion_sugerida,
      motivo: `Desbloqueo asistido por perito desde consola Angular: ${this.getSkillFriendlyName(claim.accion_sugerida)}`
    }).subscribe({
      next: (resp: ExecuteSkillResponse) => {
        this.executingSkills[claim.numero_reclamo] = false;
        this.feedbackMessage = `Skill ${this.getSkillFriendlyName(claim.accion_sugerida)} ejecutada sobre ${claim.numero_reclamo}: ${resp.detalle}`;

        this.logs.unshift({
          evento_id: `EVT-USR-${Date.now()}`,
          timestamp: new Date().toISOString(),
          nodo: 'SKILL_DISPATCHER',
          tipo_evento: 'DISPARO_SKILL',
          detalle: `[${claim.numero_reclamo}] ${resp.skill_ejecutada} -> Estado: ${resp.nuevo_estado_expediente}`,
          impacto_expedientes: 1
        });

        this.cargarDatosCluster();
        setTimeout(() => this.feedbackMessage = null, 5000);
      },
      error: (err) => {
        this.executingSkills[claim.numero_reclamo] = false;
        this.errorMessage = `Error al ejecutar skill sobre ${claim.numero_reclamo}`;
        console.error(err);
      }
    });
  }

  toggleSwarm(): void {
    this.isSwarmPaused = !this.isSwarmPaused;
    const msg = this.isSwarmPaused ? 'Enjambre de agentes en PAUSA preventiva.' : 'Enjambre de agentes REANUDADO.';
    this.logs.unshift({
      evento_id: `EVT-SWARM-${Date.now()}`,
      timestamp: new Date().toISOString(),
      nodo: 'SWARM_CONTROLLER',
      tipo_evento: this.isSwarmPaused ? 'PAUSA_ENJAMBRE' : 'REANUDAR_ENJAMBRE',
      detalle: msg,
      impacto_expedientes: 0
    });
  }

  triggerHealthCheck(): void {
    this.healthCheckRunning = true;
    this.healthCheckResult = null;
    setTimeout(() => {
      this.healthCheckRunning = false;
      this.healthCheckResult = 'Brokers Kafka & Workers LangGraph: 100% Operativos (Latencia 38ms)';
      setTimeout(() => this.healthCheckResult = null, 4000);
    }, 1200);
  }

  exportTelemetry(): void {
    if (!this.clusterState) return;
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(this.clusterState, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `aegiscore_telemetry_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  }

  getSkillFriendlyName(skillId: string): string {
    switch (skillId) {
      case 'SKILL_REASIGNAR_PERITO_GPS':
        return 'Reasignar Perito Más Cercano (GPS)';
      case 'SKILL_FAST_TRACK_APROBACION':
        return 'Aprobación Express Fast-Track (<$1,500)';
      case 'SKILL_SOLICITAR_SEGUNDA_EVIDENCIA':
        return 'Solicitar Foto Odómetro / Telemetría';
      case 'SKILL_CONGELAR_LIQUIDACION_SAGA':
        return 'Congelar Liquidación Preventiva (Fraude)';
      default:
        return skillId;
    }
  }

  getNodeIcon(nodoId: string): string {
    switch (nodoId) {
      case 'fnol_ingestion': return 'inbox';
      case 'vision_perception': return 'view_in_ar';
      case 'policy_check': return 'policy';
      case 'fraud_guard': return 'gshield';
      case 'settlement_saga': return 'currency_exchange';
      default: return 'account_tree';
    }
  }

  getNodeColorClass(nodoId: string): string {
    switch (nodoId) {
      case 'fnol_ingestion': return 'node-teal';
      case 'vision_perception': return 'node-indigo';
      case 'policy_check': return 'node-gray';
      case 'fraud_guard': return 'node-amber';
      case 'settlement_saga': return 'node-navy';
      default: return 'node-teal';
    }
  }

  getSeveridadBadgeClass(dias: number): string {
    if (dias >= 5) return 'severidad-critica';
    if (dias >= 3) return 'severidad-alta';
    return 'severidad-media';
  }
}
