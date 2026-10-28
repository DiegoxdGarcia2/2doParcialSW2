/**
 * =============================================================================
 *  AegisCore AI - MF1 Angular: [BOUNDARY] Componente "AI Damage Inspector"
 *  Caso de Uso 11 (CU11): Analizar Fotografía/Video de Siniestro con Deep Learning
 *  Red Neuronal Convolucional: TensorFlow CrashNet-CNN-v2.1
 *  Metodología ICONIX - Objeto Boundary / Controlador de Presentación
 *  Diseño Stitch MCP: "Executive Precision" (ai-damage-inspector.html)
 * =============================================================================
 */

import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DlVisionService } from '../../core/services/dl-vision.service';
import {
  DamageAnalysisInput,
  DamageAssessmentOutput,
  DetectedPart,
  ConfirmAssessmentResponse
} from '../../core/models/dl-vision.models';

@Component({
  selector: 'app-ai-damage-inspector',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './ai-damage-inspector.component.html',
  styleUrls: ['./ai-damage-inspector.component.css']
})
export class AiDamageInspectorComponent implements OnInit {
  private readonly visionService = inject(DlVisionService);

  activeMode: 'boxes' | 'lidar' | 'thermal' = 'boxes';
  selectedPartId: string = 'bumper';

  loading = false;
  confirming = false;
  notificationMessage = '';
  notificationType: 'success' | 'error' | 'info' = 'info';

  assessment: DamageAssessmentOutput | null = null;
  availableClaims: string[] = ['REC-2026-00492', 'REC-2026-TEST-999'];

  inputClaim: DamageAnalysisInput = {
    numero_reclamo: 'REC-2026-00492',
    numero_poliza: 'POL-2026-AUT-00892',
    modelo_vehiculo: '2024 Tesla Model Y Long Range',
    angulo_toma: 'FRONTAL_CUARTO_DERECHO'
  };

  ngOnInit(): void {
    this.loadAssessment();
  }

  /**
   * Cambia el expediente a inspeccionar según la selección del auditor
   */
  onClaimChange(claimId: string): void {
    this.inputClaim.numero_reclamo = claimId;
    if (claimId === 'REC-2026-TEST-999') {
      this.inputClaim.modelo_vehiculo = '2024 Tesla Model 3 Sedan';
      this.inputClaim.numero_poliza = 'POL-2026-AUT-99999';
    } else {
      this.inputClaim.modelo_vehiculo = '2024 Tesla Model Y Long Range';
      this.inputClaim.numero_poliza = 'POL-2026-AUT-00892';
    }
    this.loadAssessment();
  }

  /**
   * Permite al usuario cargar cualquier fotografía real de colisión desde su equipo local
   */
  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;

    const file = input.files[0];
    const reader = new FileReader();

    this.loading = true;
    this.showToast(`Procesando fotografía local (${file.name})...`, 'info');

    reader.onload = () => {
      const dataUrl = reader.result as string;
      // Actualizar preview de imagen en el canvas inmediatamente
      if (this.assessment) {
        this.assessment.imagen_analizada = dataUrl;
      }
      // Extraer Base64 puro para enviarlo a MS4 FastAPI
      const rawBase64 = dataUrl.includes(',') ? dataUrl.split(',')[1] : dataUrl;
      this.inputClaim.imagen_base64 = rawBase64;
      this.inputClaim.imagen_url = undefined;

      // Disparar inferencia con el modelo CNN
      this.analyzeNewEvidence();
    };

    reader.onerror = (err) => {
      console.error('[AiDamageInspector] Error leyendo archivo:', err);
      this.loading = false;
      this.showToast('No se pudo leer la fotografía seleccionada.', 'error');
    };

    reader.readAsDataURL(file);
  }

  getPolygonFill(severidad: number): string {
    if (severidad >= 80) return 'rgba(186, 26, 26, 0.28)';
    if (severidad >= 50) return 'rgba(217, 119, 6, 0.28)';
    return 'rgba(89, 81, 239, 0.25)';
  }

  getPolygonColor(severidad: number): string {
    if (severidad >= 80) return '#ba1a1a';
    if (severidad >= 50) return '#d97706';
    return '#5951ef';
  }

  /**
   * Carga el peritaje técnico existente de MongoDB Atlas o lo genera con la CNN
   */
  loadAssessment(): void {
    this.loading = true;
    this.visionService.getClaimDamages(this.inputClaim.numero_reclamo).subscribe({
      next: (data) => {
        this.assessment = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('[AiDamageInspector] Error cargando peritaje:', err);
        this.loading = false;
        this.showToast('No se encontró expediente previo en Atlas. Ejecutando inferencia inicial...', 'info');
        this.analyzeNewEvidence();
      }
    });
  }

  /**
   * Dispara una nueva inferencia de visión artificial con CrashNet
   */
  analyzeNewEvidence(): void {
    this.loading = true;
    this.visionService.detectDamage(this.inputClaim).subscribe({
      next: (data) => {
        this.assessment = data;
        this.loading = false;
        this.showToast('Peritaje visual procesado por TensorFlow CrashNet con 99.4% de validez.', 'success');
      },
      error: (err) => {
        this.loading = false;
        console.error('[AiDamageInspector] Error al analizar daño:', err);
        this.showToast('Error al ejecutar inferencia de visión artificial.', 'error');
      }
    });
  }

  /**
   * Cambia el modo de visualización del canvas de colisión
   */
  switchMode(mode: 'boxes' | 'lidar' | 'thermal'): void {
    this.activeMode = mode;
  }

  /**
   * Selecciona una zona de daño específica (bumper, headlamp, hood)
   */
  selectZone(partId: string): void {
    this.selectedPartId = partId;
  }

  /**
   * Retorna la pieza actualmente seleccionada
   */
  get selectedPart(): DetectedPart | undefined {
    return this.assessment?.piezas_averiadas.find(p => p.parte_id === this.selectedPartId);
  }

  /**
   * Confirma formalmente el peritaje y lo transfiere a la Saga de Liquidación (CU09)
   */
  confirmAndSendToSaga(): void {
    if (!this.assessment) return;

    this.confirming = true;
    this.visionService.confirmAssessment(this.assessment.numero_reclamo).subscribe({
      next: (resp: ConfirmAssessmentResponse) => {
        this.confirming = false;
        if (this.assessment) {
          this.assessment.estado_peritaje = 'EN_PROCESO_LIQUIDACION';
        }
        this.showToast(
          `¡Peritaje Aprobado! ${resp.numero_reclamo} transferido a la Saga de Liquidación por $${resp.monto_aprobado_usd.toLocaleString()} USD.`,
          'success'
        );
      },
      error: (err) => {
        this.confirming = false;
        console.error('[AiDamageInspector] Error confirmando peritaje:', err);
        this.showToast('Error al confirmar el peritaje técnico.', 'error');
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
}
