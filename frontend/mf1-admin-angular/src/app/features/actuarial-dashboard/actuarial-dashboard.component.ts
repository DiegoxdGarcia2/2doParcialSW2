/**
 * =============================================================================
 *  AegisCore AI - MF1 Angular: [BOUNDARY] Componente Dashboard Actuarial
 *  Metodología ICONIX - Vista / Controlador de Presentación para CU12
 * =============================================================================
 */

import { Component, OnInit, OnDestroy, ElementRef, ViewChild, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Chart, registerables } from 'chart.js';
import { MlActuarialService } from '../../core/services/ml-actuarial.service';
import {
  PredictionInput,
  PredictionOutput,
  ModelMetrics,
  RetrainResponse
} from '../../core/models/ml-actuarial.models';

Chart.register(...registerables);

@Component({
  selector: 'app-actuarial-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './actuarial-dashboard.component.html',
  styleUrls: ['./actuarial-dashboard.component.css']
})
export class ActuarialDashboardComponent implements OnInit, OnDestroy {
  private readonly mlService = inject(MlActuarialService);

  @ViewChild('salesChart') salesChartRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('featureChart') featureChartRef!: ElementRef<HTMLCanvasElement>;

  salesChartInstance: Chart | null = null;
  featureChartInstance: Chart | null = null;

  loading = false;
  retraining = false;
  notificationMessage = '';
  notificationType: 'success' | 'error' | 'info' = 'info';

  activeScenario = 'baseline';
  selectedTimeHorizon = 'Q3 2026 (Forecast)';

  // Parámetros de simulación reactivos
  input: PredictionInput = {
    edad_asegurado: 34,
    antiguedad_licencia_anios: 12,
    tipo_vehiculo: 'SUV',
    anio_vehiculo: 2021,
    valor_comercial_usd: 28000,
    historial_siniestros_previos: 1,
    perfil_riesgo_score: 45,
    meses_a_proyectar: 6
  };

  result: PredictionOutput | null = null;
  metrics: ModelMetrics | null = null;

  vehicleTypes = [
    { id: 'SUV', label: 'SUV', icon: 'directions_car' },
    { id: 'CAMIONETA', label: 'Camioneta', icon: 'local_shipping' },
    { id: 'SEDAN', label: 'Sedán', icon: 'airport_shuttle' },
    { id: 'HATCHBACK', label: 'Hatchback', icon: 'minor_crash' },
    { id: 'MOTOCICLETA', label: 'Moto', icon: 'two_wheeler' }
  ];

  ngOnInit(): void {
    this.cargarMetricasEInferenciaInicial();
  }

  ngOnDestroy(): void {
    this.destroyCharts();
  }

  private destroyCharts(): void {
    if (this.salesChartInstance) {
      this.salesChartInstance.destroy();
      this.salesChartInstance = null;
    }
    if (this.featureChartInstance) {
      this.featureChartInstance.destroy();
      this.featureChartInstance = null;
    }
  }

  cargarMetricasEInferenciaInicial(): void {
    this.loading = true;
    this.mlService.getModelMetrics().subscribe({
      next: (m) => {
        this.metrics = m;
        this.ejecutarInferencia();
      },
      error: (err) => {
        console.error('Error al cargar métricas:', err);
        this.loading = false;
        this.mostrarNotificacion('Conectando con MS4 FastAPI...', 'info');
        this.ejecutarInferencia();
      }
    });
  }

  ejecutarInferencia(): void {
    this.loading = true;
    this.mlService.predictSalesAndPremium(this.input).subscribe({
      next: (res) => {
        this.result = res;
        this.loading = false;
        setTimeout(() => {
          this.renderizarGraficoVentas();
          this.renderizarGraficoFeatureImportance();
        }, 100);
      },
      error: (err) => {
        this.loading = false;
        this.mostrarNotificacion('Error al calcular inferencia actuarial. Revisa la conexión con MS4.', 'error');
      }
    });
  }

  reentrenarModelo(): void {
    this.retraining = true;
    this.mostrarNotificacion('Reentrenando ensamble Random Forest contra Neon PostgreSQL...', 'info');
    this.mlService.retrainModels().subscribe({
      next: (res: RetrainResponse) => {
        this.retraining = false;
        this.mostrarNotificacion(
          `¡Reentrenamiento completado! R²: ${res.r2_score_nuevo} | MAE: $${res.mae_usd_nuevo} USD (${res.registros_cargados} registros en ${res.tiempo_ejecucion_segundos}s)`,
          'success'
        );
        this.cargarMetricasEInferenciaInicial();
      },
      error: (err) => {
        this.retraining = false;
        this.mostrarNotificacion('Error al reentrenar modelo. Verifica la base de datos.', 'error');
      }
    });
  }

  seleccionarEscenario(escenario: string): void {
    this.activeScenario = escenario;
    if (escenario === 'baseline') {
      this.input = {
        edad_asegurado: 38,
        antiguedad_licencia_anios: 15,
        tipo_vehiculo: 'SUV',
        anio_vehiculo: 2021,
        valor_comercial_usd: 26000,
        historial_siniestros_previos: 0,
        perfil_riesgo_score: 30,
        meses_a_proyectar: 6
      };
    } else if (escenario === 'joven_riesgo') {
      this.input = {
        edad_asegurado: 21,
        antiguedad_licencia_anios: 2,
        tipo_vehiculo: 'HATCHBACK',
        anio_vehiculo: 2017,
        valor_comercial_usd: 14000,
        historial_siniestros_previos: 2,
        perfil_riesgo_score: 75,
        meses_a_proyectar: 6
      };
    } else if (escenario === 'flota_comercial') {
      this.input = {
        edad_asegurado: 48,
        antiguedad_licencia_anios: 25,
        tipo_vehiculo: 'CAMIONETA',
        anio_vehiculo: 2023,
        valor_comercial_usd: 48000,
        historial_siniestros_previos: 1,
        perfil_riesgo_score: 40,
        meses_a_proyectar: 6
      };
    }
    this.ejecutarInferencia();
  }

  seleccionarVehiculo(tipo: string): void {
    this.input.tipo_vehiculo = tipo;
    this.ejecutarInferencia();
  }

  mostrarNotificacion(msg: string, type: 'success' | 'error' | 'info' = 'info'): void {
    this.notificationMessage = msg;
    this.notificationType = type;
    setTimeout(() => {
      this.notificationMessage = '';
    }, 6000);
  }

  renderizarGraficoVentas(): void {
    if (!this.result || !this.salesChartRef) return;

    const ctx = this.salesChartRef.nativeElement.getContext('2d');
    if (!ctx) return;

    if (this.salesChartInstance) {
      this.salesChartInstance.destroy();
    }

    const labels = this.result.proyecciones_mensuales.map(p => p.mes);
    const salesData = this.result.proyecciones_mensuales.map(p => p.ventas_estimadas_polizas);
    const premiumData = this.result.proyecciones_mensuales.map(p => p.prima_sugerida_usd);
    const confMin = this.result.proyecciones_mensuales.map(p => p.intervalo_confianza_min);
    const confMax = this.result.proyecciones_mensuales.map(p => p.intervalo_confianza_max);

    this.salesChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Demanda de Pólizas Proyectada',
            data: salesData,
            borderColor: '#005c55',
            backgroundColor: 'rgba(0, 92, 85, 0.12)',
            fill: true,
            tension: 0.35,
            borderWidth: 3,
            yAxisID: 'y'
          },
          {
            label: 'Prima Óptima Sugerida ($ USD)',
            data: premiumData,
            borderColor: '#3f33d6',
            backgroundColor: 'transparent',
            borderDash: [5, 5],
            borderWidth: 2,
            tension: 0.2,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false
        },
        plugins: {
          legend: {
            position: 'top',
            labels: {
              boxWidth: 14,
              font: { family: 'Inter', size: 12 }
            }
          },
          tooltip: {
            padding: 12,
            backgroundColor: '#0f172a',
            titleFont: { family: 'Plus Jakarta Sans', size: 13, weight: 'bold' },
            bodyFont: { family: 'JetBrains Mono', size: 12 }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { font: { family: 'JetBrains Mono', size: 11 } }
          },
          y: {
            type: 'linear',
            display: true,
            position: 'left',
            title: { display: true, text: 'Pólizas Vendidas / Mes', font: { family: 'Inter', size: 11 } },
            grid: { color: 'rgba(203, 219, 245, 0.3)' }
          },
          y1: {
            type: 'linear',
            display: true,
            position: 'right',
            title: { display: true, text: 'Prima Promedio ($ USD)', font: { family: 'Inter', size: 11 } },
            grid: { drawOnChartArea: false }
          }
        }
      }
    });
  }

  renderizarGraficoFeatureImportance(): void {
    if (!this.featureChartRef) return;
    const featList = this.result?.metricas_modelo?.feature_importances || this.metrics?.feature_importances;
    if (!featList || featList.length === 0) return;

    const ctx = this.featureChartRef.nativeElement.getContext('2d');
    if (!ctx) return;

    if (this.featureChartInstance) {
      this.featureChartInstance.destroy();
    }

    const topFeats = featList.slice(0, 6);
    const labels = topFeats.map(f => f.variable);
    const data = topFeats.map(f => f.importancia_porcentaje);

    this.featureChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Ponderación Explicable (%)',
          data,
          backgroundColor: [
            '#005c55',
            '#0f766e',
            '#3f33d6',
            '#5951ef',
            '#565e74',
            '#80d5cb'
          ],
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0f172a',
            bodyFont: { family: 'JetBrains Mono' }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            max: Math.max(...data) + 5,
            ticks: {
              callback: (val) => `${val}%`,
              font: { family: 'JetBrains Mono', size: 11 }
            },
            grid: { color: 'rgba(203, 219, 245, 0.3)' }
          },
          y: {
            ticks: { font: { family: 'Inter', size: 12, weight: 'bold' } },
            grid: { display: false }
          }
        }
      }
    });
  }
}
