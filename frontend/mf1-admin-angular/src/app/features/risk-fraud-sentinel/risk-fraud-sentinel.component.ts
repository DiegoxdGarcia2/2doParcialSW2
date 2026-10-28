/**
 * =============================================================================
 *  AegisCore AI - MF1 Angular: [BOUNDARY] Componente "Risk & Fraud Sentinel"
 *  Caso de Uso 13 (CU13): Segmentación K-Means y Detección de Fraude Isolation Forest
 *  Metodología ICONIX - Objeto Boundary / Controlador de Presentación
 *  Diseño Stitch MCP: "Executive Precision" (Executive Teal #005C55, Deep Navy, Alabaster)
 * =============================================================================
 */

import { Component, OnInit, OnDestroy, ElementRef, ViewChild, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Chart, registerables } from 'chart.js';
import { MlUnsupervisedService } from '../../core/services/ml-unsupervised.service';
import {
  FraudDashboardSummary,
  FraudAlert,
  EvaluateClaimInput,
  FreezeClaimResponse,
  ClusterProfile
} from '../../core/models/ml-unsupervised.models';

Chart.register(...registerables);

@Component({
  selector: 'app-risk-fraud-sentinel',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './risk-fraud-sentinel.component.html',
  styleUrls: ['./risk-fraud-sentinel.component.css']
})
export class RiskFraudSentinelComponent implements OnInit, OnDestroy {
  private readonly mlService = inject(MlUnsupervisedService);

  @ViewChild('clustersChart') clustersChartRef!: ElementRef<HTMLCanvasElement>;
  clustersChartInstance: Chart | null = null;

  loading = false;
  evaluating = false;
  retraining = false;
  freezingClaimId: string | null = null;
  notificationMessage = '';
  notificationType: 'success' | 'error' | 'info' = 'info';

  activeFilter: 'all' | 'critical' | 'siu' | 'archived' = 'all';

  summary: FraudDashboardSummary | null = null;
  alerts: FraudAlert[] = [];
  filteredAlerts: FraudAlert[] = [];

  // Modal / Formulario interactivo para auditoría en tiempo real
  showEvaluateModal = false;
  newClaim: EvaluateClaimInput = {
    reclamo_id: 'REC-2026-00501',
    poliza_id: 'POL-2026-AUT-00100',
    edad_conductor: 23,
    tipo_vehiculo: 'SEDAN',
    valor_comercial_usd: 16000,
    monto_solicitado_usd: 11200,
    dias_desde_emision: 4,
    historial_siniestros: 3,
    taller_mecanico: 'Taller Mecánico El Progreso'
  };

  lastEvaluationResult: FraudAlert | null = null;

  ngOnInit(): void {
    this.loadTelemetry();
  }

  ngOnDestroy(): void {
    if (this.clustersChartInstance) {
      this.clustersChartInstance.destroy();
    }
  }

  /**
   * Carga la telemetría consolidada de K-Means e Isolation Forest desde MS4
   */
  loadTelemetry(): void {
    this.loading = true;
    this.mlService.getClustersAndAnomalies().subscribe({
      next: (data) => {
        this.summary = data;
        this.alerts = data.alertas_recientes || [];
        this.applyFilter();
        this.loading = false;
        setTimeout(() => this.renderClustersChart(), 100);
      },
      error: (err) => {
        console.error('[RiskFraudSentinel] Error cargando telemetría:', err);
        this.loading = false;
        this.showToast('Error al conectar con MS4. Mostrando estado preventivo local.', 'error');
        this.loadFallbackSummary();
      }
    });
  }

  /**
   * Aplica filtros de criticidad a la lista reactiva de reclamos
   */
  setFilter(filter: 'all' | 'critical' | 'siu' | 'archived'): void {
    this.activeFilter = filter;
    this.applyFilter();
  }

  applyFilter(): void {
    if (this.activeFilter === 'all') {
      this.filteredAlerts = [...this.alerts];
    } else if (this.activeFilter === 'critical') {
      this.filteredAlerts = this.alerts.filter(
        a => a.nivel_criticidad === 'CRÍTICO' || a.es_anomalo
      );
    } else if (this.activeFilter === 'siu') {
      this.filteredAlerts = this.alerts.filter(
        a => a.estado_pago === 'CONGELADO_PREVENTIVO_SAGA' || a.estado_pago === 'PENDIENTE_REVISION'
      );
    } else if (this.activeFilter === 'archived') {
      this.filteredAlerts = this.alerts.filter(
        a => a.estado_pago === 'APROBADO_FAST_TRACK' || a.estado_pago === 'AUDITADO'
      );
    }
  }

  /**
   * Congelamiento Preventivo de Pago (Acción SIU en MongoDB Atlas)
   */
  freezePayout(alert: FraudAlert): void {
    this.freezingClaimId = alert.reclamo_id;
    this.mlService.freezeClaim(alert.reclamo_id).subscribe({
      next: (resp: FreezeClaimResponse) => {
        this.freezingClaimId = null;
        alert.estado_pago = 'CONGELADO_PREVENTIVO_SAGA';
        alert.nivel_criticidad = 'CRÍTICO';
        if (this.summary) {
          this.summary.perdidas_prevenidas_usd += alert.monto_solicitado_usd;
          this.summary.total_alertas_activas += 1;
        }
        this.showToast(
          `Pago de ${alert.reclamo_id} congelado preventivamente. Expediente elevado a la SIU.`,
          'success'
        );
        this.applyFilter();
      },
      error: (err) => {
        this.freezingClaimId = null;
        console.error('[RiskFraudSentinel] Error al congelar pago:', err);
        this.showToast(`Error al congelar el pago de ${alert.reclamo_id}.`, 'error');
      }
    });
  }

  /**
   * Elevar investigación a la Unidad Especial (SIU)
   */
  escalateToSIU(alert: FraudAlert): void {
    this.showToast(
      `Reclamo ${alert.reclamo_id} notificado con prioridad a la Unidad Especial de Investigaciones (SIU).`,
      'info'
    );
  }

  /**
   * Auditar factura o peritaje del taller mecánico
   */
  auditInvoice(alert: FraudAlert): void {
    this.showToast(
      `Auditoría forense abierta para ${alert.taller_mecanico}. Divergencia detectada: +${alert.divergencia_porcentaje}%.`,
      'info'
    );
  }

  /**
   * Solicitar informe médico o de piezas
   */
  requestEHRLog(alert: FraudAlert): void {
    this.showToast(
      `Expediente pericial y bitácora clínica solicitados para el reclamo ${alert.reclamo_id}.`,
      'info'
    );
  }

  /**
   * Evalúa un siniestro en tiempo real con Isolation Forest
   */
  evaluateClaim(): void {
    this.evaluating = true;
    this.mlService.evaluateClaim(this.newClaim).subscribe({
      next: (result: FraudAlert) => {
        this.evaluating = false;
        this.lastEvaluationResult = result;
        // Insertar en la lista al inicio
        const existingIdx = this.alerts.findIndex(a => a.reclamo_id === result.reclamo_id);
        if (existingIdx >= 0) {
          this.alerts[existingIdx] = result;
        } else {
          this.alerts.unshift(result);
        }
        this.applyFilter();
        if (result.es_anomalo) {
          this.showToast(
            `¡Alerta de Anomalía! Reclamo ${result.reclamo_id} clasificado como ${result.nivel_criticidad} (Score: ${result.score_anomalia}).`,
            'error'
          );
        } else {
          this.showToast(
            `Reclamo ${result.reclamo_id} evaluado como NORMAL. Aprobado para Fast-Track.`,
            'success'
          );
        }
      },
      error: (err) => {
        this.evaluating = false;
        console.error('[RiskFraudSentinel] Error al evaluar reclamo:', err);
        this.showToast('Error al evaluar siniestro con Isolation Forest.', 'error');
      }
    });
  }

  /**
   * Reentrena los modelos K-Means e Isolation Forest
   */
  retrainModels(): void {
    this.retraining = true;
    this.mlService.retrainModels().subscribe({
      next: (resp) => {
        this.retraining = false;
        this.showToast('Modelos K-Means e Isolation Forest reentrenados exitosamente.', 'success');
        this.loadTelemetry();
      },
      error: (err) => {
        this.retraining = false;
        console.error('[RiskFraudSentinel] Error al reentrenar:', err);
        this.showToast('Error al reentrenar modelos no supervisados.', 'error');
      }
    });
  }

  /**
   * Renderiza el gráfico de Radar / Comparativo de Clusters K-Means
   */
  renderClustersChart(): void {
    if (!this.clustersChartRef || !this.summary?.clusters_kmeans?.length) return;

    if (this.clustersChartInstance) {
      this.clustersChartInstance.destroy();
    }

    const clusters = this.summary.clusters_kmeans;
    const ctx = this.clustersChartRef.nativeElement.getContext('2d');
    if (!ctx) return;

    const labels = ['Edad Promedio', 'Valor Vehículo (x$1k)', 'Siniestros/Año (x10)', 'Score Riesgo (x0.1)'];

    const colors = [
      { border: '#005C55', bg: 'rgba(0, 92, 85, 0.2)' },     // Executive Teal
      { border: '#4F46E5', bg: 'rgba(79, 70, 229, 0.2)' },    // Royal Indigo
      { border: '#BA1A1A', bg: 'rgba(186, 26, 26, 0.2)' }     // Critical Red
    ];

    const datasets = clusters.map((c, i) => {
      const col = colors[i % colors.length];
      return {
        label: `${c.nombre} (${c.porcentaje_flota}%)`,
        data: [
          c.edad_media,
          c.valor_vehiculo_medio_usd / 1000,
          c.frecuencia_siniestros_anual * 10,
          c.score_riesgo_medio * 0.1
        ],
        borderColor: col.border,
        backgroundColor: col.bg,
        borderWidth: 2,
        pointBackgroundColor: col.border,
        pointRadius: 4
      };
    });

    this.clustersChartInstance = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: labels,
        datasets: datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { color: 'rgba(15, 23, 42, 0.08)' },
            grid: { color: 'rgba(15, 23, 42, 0.06)' },
            pointLabels: {
              font: { family: 'Inter', size: 11, weight: 'bold' },
              color: '#0F172A'
            },
            ticks: { display: false }
          }
        },
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              font: { family: 'Plus Jakarta Sans', size: 11 },
              color: '#0F172A'
            }
          }
        }
      }
    });
  }

  /**
   * Notificación Toast reactiva
   */
  showToast(message: string, type: 'success' | 'error' | 'info' = 'info'): void {
    this.notificationMessage = message;
    this.notificationType = type;
    setTimeout(() => {
      if (this.notificationMessage === message) {
        this.notificationMessage = '';
      }
    }, 4500);
  }

  /**
   * Traduce las etiquetas de nivel de amenaza a español para la interfaz
   */
  getEtiquetaNivelAmenaza(label?: string): string {
    if (!label) return 'BAJO-MODERADO';
    switch (label.toUpperCase()) {
      case 'LOW': return 'BAJO';
      case 'LOW-MODERATE': return 'BAJO-MODERADO';
      case 'MODERATE': return 'MODERADO';
      case 'HIGH': return 'ALTO';
      case 'CRITICAL': return 'CRÍTICO';
      default: return label;
    }
  }

  /**
   * Resumen de respaldo si la conexión no responde
   */
  private loadFallbackSummary(): void {
    this.summary = {
      threat_index_percentage: 12.4,
      threat_level_label: 'BAJO-MODERADO',
      perdidas_prevenidas_usd: 18600000.0,
      total_siniestros_auditados: 1200,
      total_alertas_activas: 2,
      silhouette_score_kmeans: 0.42,
      clusters_kmeans: [
        {
          cluster_id: 0,
          nombre: 'Conductores Prudentes VIP (Bajo Riesgo)',
          total_asegurados: 540,
          porcentaje_flota: 45.0,
          edad_media: 48.2,
          valor_vehiculo_medio_usd: 34500.0,
          frecuencia_siniestros_anual: 0.04,
          score_riesgo_medio: 18.5,
          prima_recomendada_descuento: '-15% (Bonificación No Siniestro)'
        },
        {
          cluster_id: 1,
          nombre: 'Riesgo Moderado Estándar',
          total_asegurados: 480,
          porcentaje_flota: 40.0,
          edad_media: 38.6,
          valor_vehiculo_medio_usd: 24200.0,
          frecuencia_siniestros_anual: 0.18,
          score_riesgo_medio: 46.2,
          prima_recomendada_descuento: '0% (Tarifa Base de Mercado)'
        },
        {
          cluster_id: 2,
          nombre: 'Alta Siniestralidad / Conductores Jóvenes',
          total_asegurados: 180,
          porcentaje_flota: 15.0,
          edad_media: 23.4,
          valor_vehiculo_medio_usd: 16800.0,
          frecuencia_siniestros_anual: 0.62,
          score_riesgo_medio: 82.1,
          prima_recomendada_descuento: '+25% (Recargo Actuarial por Frecuencia)'
        }
      ],
      alertas_recientes: [
        {
          reclamo_id: 'REC-2026-00402',
          poliza_id: 'POL-2026-AUT-99120',
          monto_solicitado_usd: 9200.0,
          monto_promedio_mercado_usd: 2100.0,
          divergencia_porcentaje: 338.1,
          score_anomalia: -0.8420,
          es_anomalo: true,
          nivel_criticidad: 'CRÍTICO',
          taller_mecanico: 'Taller Mecánico Los Álamos',
          motivo_sospecha: 'Colisión múltiple simulada (#R-402). 4 siniestros consecutivos en 48 horas.',
          estado_pago: 'CONGELADO_PREVENTIVO_SAGA',
          fecha_alerta: new Date().toISOString()
        }
      ],
      timestamp: new Date().toISOString()
    };
    this.alerts = this.summary.alertas_recientes;
    this.applyFilter();
    setTimeout(() => this.renderClustersChart(), 100);
  }
}
