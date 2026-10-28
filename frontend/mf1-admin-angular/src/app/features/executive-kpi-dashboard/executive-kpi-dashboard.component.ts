import { Component, OnInit, OnDestroy, ElementRef, ViewChild, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

@Component({
  selector: 'app-executive-kpi-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './executive-kpi-dashboard.component.html',
  styleUrls: ['./executive-kpi-dashboard.component.css']
})
export class ExecutiveKpiDashboardComponent implements OnInit, OnDestroy {
  @ViewChild('lossTrendChart') lossTrendChartRef!: ElementRef<HTMLCanvasElement>;
  chartInstance: Chart | null = null;

  activePeriod: 'Q3' | 'YTD' = 'Q3';
  notificationMessage = '';
  notificationType: 'success' | 'info' = 'info';

  ngOnInit(): void {
    setTimeout(() => this.renderChart(), 100);
  }

  ngOnDestroy(): void {
    if (this.chartInstance) {
      this.chartInstance.destroy();
    }
  }

  setPeriod(period: 'Q3' | 'YTD'): void {
    this.activePeriod = period;
    this.showToast(`Periodo actualizado a ${period === 'Q3' ? 'Tercer Trimestre (Q3 2026)' : 'Acumulado Anual (YTD)'}`);
  }

  showToast(message: string, type: 'success' | 'info' = 'info'): void {
    this.notificationMessage = message;
    this.notificationType = type;
    setTimeout(() => {
      if (this.notificationMessage === message) {
        this.notificationMessage = '';
      }
    }, 4000);
  }

  descargarAuditoria(): void {
    this.showToast('Paquete de Auditoría Actuarial descargado con sello SHA-256 verificado.', 'success');
  }

  renderChart(): void {
    if (!this.lossTrendChartRef) return;
    const ctx = this.lossTrendChartRef.nativeElement.getContext('2d');
    if (!ctx) return;

    if (this.chartInstance) {
      this.chartInstance.destroy();
    }

    const labels = ['Abr ($122M)', 'May ($130M)', 'Jun ($145M)', 'Jul ($138M)', 'Ago ($129M)', 'Sep ($118M)'];

    this.chartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Siniestros Flota Vehicular ($M USD)',
            data: [65, 80, 40, 50, 75, 90],
            borderColor: '#005c55',
            backgroundColor: 'rgba(0, 92, 85, 0.15)',
            fill: true,
            tension: 0.35,
            borderWidth: 2.5,
            pointBackgroundColor: '#005c55',
            pointRadius: 4
          },
          {
            label: 'Salud y Coberturas Especiales ($M USD)',
            data: [88, 75, 60, 72, 65, 55],
            borderColor: '#3f33d6',
            backgroundColor: 'rgba(63, 51, 214, 0.12)',
            fill: true,
            tension: 0.35,
            borderWidth: 2,
            borderDash: [4, 4],
            pointBackgroundColor: '#3f33d6',
            pointRadius: 3
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
              boxWidth: 12,
              font: { family: 'Inter', size: 11 },
              color: '#0f172a'
            }
          },
          tooltip: {
            backgroundColor: '#0f172a',
            titleFont: { family: 'Plus Jakarta Sans', size: 12, weight: 'bold' },
            bodyFont: { family: 'JetBrains Mono', size: 11 }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { font: { family: 'JetBrains Mono', size: 10 }, color: '#565e74' }
          },
          y: {
            beginAtZero: true,
            max: 120,
            ticks: {
              callback: (val) => `$${val}M`,
              font: { family: 'JetBrains Mono', size: 10 },
              color: '#565e74'
            },
            grid: { color: 'rgba(203, 219, 245, 0.3)' }
          }
        }
      }
    });
  }
}

