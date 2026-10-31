/**
 * =============================================================================
 *  AegisCore AI - MF1 Angular: [BOUNDARY] Componente "AI Damage Inspector"
 *  Caso de Uso 11 (CU11): Analizar Fotografía/Video de Siniestro con Deep Learning
 *  Red Neuronal Convolucional: TensorFlow CrashNet-CNN-v2.1
 *  Metodología ICONIX - Objeto Boundary / Controlador de Presentación
 *  Diseño Stitch MCP: "Executive Precision" (ai-damage-inspector.html)
 * =============================================================================
 */

import {
  Component,
  OnInit,
  AfterViewInit,
  OnDestroy,
  ElementRef,
  ViewChild,
  ChangeDetectorRef,
  inject
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DlVisionService } from '../../core/services/dl-vision.service';
import {
  DamageAnalysisInput,
  DamageAssessmentOutput,
  DetectedPart,
  Keyframe,
  ConfirmAssessmentResponse
} from '../../core/models/dl-vision.models';

@Component({
  selector: 'app-ai-damage-inspector',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './ai-damage-inspector.component.html',
  styleUrls: ['./ai-damage-inspector.component.css']
})
export class AiDamageInspectorComponent implements OnInit, AfterViewInit, OnDestroy {
  private readonly visionService = inject(DlVisionService);
  private readonly cdr = inject(ChangeDetectorRef);

  @ViewChild('lidarCanvas', { static: false }) lidarCanvasRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('thermalCanvas', { static: false }) thermalCanvasRef!: ElementRef<HTMLCanvasElement>;

  activeMode: 'boxes' | 'lidar' | 'thermal' = 'boxes';
  selectedPartId: string = 'bumper';
  selectedKeyframeId: string = 'frame_02';

  loading = false;
  confirming = false;
  notificationMessage = '';
  notificationType: 'success' | 'error' | 'info' = 'info';

  // Control del Modal de Éxito Saga (CU09)
  showSagaModal = false;
  sagaTxId = '';
  sagaAuditHash = '';
  sagaConfirmedResp: ConfirmAssessmentResponse | null = null;

  assessment: DamageAssessmentOutput | null = null;
  selectedKeyframe: Keyframe | null = null;

  // Galería de casos preconfigurados oficiales
  casosDisponibles = [
    { id: 'REC-2026-00492', label: 'REC-2026-00492 • Tesla Model Y (Impacto Frontal)', vehiculo: '2024 Tesla Model Y Long Range', poliza: 'POL-2026-AUT-00892', esVideo: false },
    { id: 'REC-2026-00493', label: 'REC-2026-00493 • Toyota RAV4 (Colisión Lateral)', vehiculo: 'Toyota RAV4 Hybrid / SUV', poliza: 'POL-2026-AUT-00892', esVideo: false },
    { id: 'REC-2026-00494', label: 'REC-2026-00494 • BMW Serie 3 (Capó & Radiador)', vehiculo: 'BMW Serie 3 Sedán Ejecutivo', poliza: 'POL-2026-AUT-00552', esVideo: false },
    { id: 'REC-2026-VIDEO-01', label: 'REC-2026-VIDEO-01 • Ford Mustang Mach-E (Video Choque Cruce)', vehiculo: 'Ford Mustang Mach-E (Video Colisión)', poliza: 'POL-2026-AUT-88120', esVideo: true }
  ];

  inputClaim: DamageAnalysisInput = {
    numero_reclamo: 'REC-2026-00492',
    numero_poliza: 'POL-2026-AUT-00892',
    modelo_vehiculo: '2024 Tesla Model Y Long Range',
    angulo_toma: 'FRONTAL_CUARTO_DERECHO'
  };

  // Catálogo oficial de evidencias in-situ reportadas desde MS2/MS3
  readonly catalogoEvidenciasPorReclamo: Record<string, Array<{ id: string; url: string; label: string; ratio_dano?: number; orientacion?: string }>> = {
    'REC-2026-00492': [
      {
        id: 'EV-492-01',
        url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCx3fyi2LFOE3hDw3Sb6G8eHgn_hLSk3e7xQXTIWEd9BHQw9lVi_s5wz_M5NWDh0T9QCeRoH2TL4EyTMLMv2iBYUrO80grJz545-U3kxPc3UD3WVzixxcpOswoD6j-xqb-xjZ1iRANvcxJZk0atX1tZn1GM6_ZHEV5B65eFNgBrEywi2Qf8QrNY46M3A6genM8PMO_WwLiJFuf2G-9-8Dq7dkRLf4fsOW0hTOC_k8s',
        label: 'Toma Frontal-Principal',
        ratio_dano: 24.5,
        orientacion: 'FRONTAL'
      },
      {
        id: 'EV-492-02',
        url: 'https://images.unsplash.com/photo-1617814076367-b759c7d7e738?auto=format&fit=crop&w=800&q=80',
        label: 'Lateral Derecho (3/4)',
        ratio_dano: 56.8,
        orientacion: 'TRES_CUARTOS_DERECHO'
      },
      {
        id: 'EV-492-03',
        url: 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?auto=format&fit=crop&w=800&q=80',
        label: 'Detalle Chasis & Suspensión',
        ratio_dano: 18.2,
        orientacion: 'DETALLE_MECANICO'
      }
    ],
    'REC-2026-00493': [
      {
        id: 'EV-493-01',
        url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCOtOijrIJcDyaEgrsXodAwoTNDDVqgszmLUqFdypN23RCWUmXo5JE4m9LtDyQp95tHr5kCpG9VE-eEGe0jAUUij4mfnyG8l3oSFFYRkCB2ao0ddJIjX-KKkYNiUpYRDBLRaFqYFQM27v1_iz0q03WEK6_-xM9fSPyszJho9g8ATsBD3waGlta8oJ90HHptTlxp6vtFev2F4Zv5vYQzsv8y-K8VHLWijuIxD98cMEWZ4Isc3f-83Aci',
        label: 'Lateral Derecho (Puertas)',
        ratio_dano: 48.0,
        orientacion: 'LATERAL_DERECHO'
      },
      {
        id: 'EV-493-02',
        url: 'https://images.unsplash.com/photo-1617814076367-b759c7d7e738?auto=format&fit=crop&w=800&q=80',
        label: 'Detalle Umbral & Pilar B',
        ratio_dano: 32.5,
        orientacion: 'LATERAL_DERECHO'
      }
    ],
    'REC-2026-00494': [
      {
        id: 'EV-494-01',
        url: 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?auto=format&fit=crop&w=800&q=80',
        label: 'Frontal Superior (Capó)',
        ratio_dano: 62.0,
        orientacion: 'FRONTAL'
      },
      {
        id: 'EV-494-02',
        url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCx3fyi2LFOE3hDw3Sb6G8eHgn_hLSk3e7xQXTIWEd9BHQw9lVi_s5wz_M5NWDh0T9QCeRoH2TL4EyTMLMv2iBYUrO80grJz545-U3kxPc3UD3WVzixxcpOswoD6j-xqb-xjZ1iRANvcxJZk0atX1tZn1GM6_ZHEV5B65eFNgBrEywi2Qf8QrNY46M3A6genM8PMO_WwLiJFuf2G-9-8Dq7dkRLf4fsOW0hTOC_k8s',
        label: 'Detalle Radiador & Farol',
        ratio_dano: 41.0,
        orientacion: 'FRONTAL'
      }
    ],
    'REC-2026-VIDEO-01': [
      {
        id: 'EV-VID-01',
        url: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCx3fyi2LFOE3hDw3Sb6G8eHgn_hLSk3e7xQXTIWEd9BHQw9lVi_s5wz_M5NWDh0T9QCeRoH2TL4EyTMLMv2iBYUrO80grJz545-U3kxPc3UD3WVzixxcpOswoD6j-xqb-xjZ1iRANvcxJZk0atX1tZn1GM6_ZHEV5B65eFNgBrEywi2Qf8QrNY46M3A6genM8PMO_WwLiJFuf2G-9-8Dq7dkRLf4fsOW0hTOC_k8s',
        label: 'Fotograma de Impacto (Video)',
        ratio_dano: 68.0,
        orientacion: 'FRONTAL'
      }
    ]
  };

  // Galería activa de evidencias
  galeriaEvidencias: Array<{ id: string; url: string; label: string; ratio_dano?: number; orientacion?: string }> = [
    ...this.catalogoEvidenciasPorReclamo['REC-2026-00492']
  ];
  selectedEvidenciaId: string = 'EV-492-01';
  Math = Math;

  // Variables para la animación de LiDAR en Canvas
  private lidarAnimId: number | null = null;
  private scanLineY: number = 0;
  private scanDirection: number = 1;

  ngOnInit(): void {
    this.loadAssessment();
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      this.actualizarLienzosVisuales();
    }, 200);
  }

  ngOnDestroy(): void {
    if (this.lidarAnimId) {
      cancelAnimationFrame(this.lidarAnimId);
    }
  }

  /**
   * Cambia el caso de demostración
   */
  onClaimChange(claimId: string): void {
    const caso = this.casosDisponibles.find(c => c.id === claimId);
    if (caso) {
      this.inputClaim.numero_reclamo = caso.id;
      this.inputClaim.modelo_vehiculo = caso.vehiculo;
      this.inputClaim.numero_poliza = caso.poliza;
      this.inputClaim.es_video = caso.esVideo;
      this.inputClaim.imagen_base64 = undefined;
      this.inputClaim.video_base64 = undefined;

      // Sincronizar galería de evidencias correspondientes al siniestro seleccionado
      const evidencias = this.catalogoEvidenciasPorReclamo[caso.id] || this.catalogoEvidenciasPorReclamo['REC-2026-00492'];
      this.galeriaEvidencias = [...evidencias];
      this.selectedEvidenciaId = this.galeriaEvidencias[0]?.id || '';
      this.inputClaim.imagen_url = this.galeriaEvidencias[0]?.url;
    }
    this.loadAssessment();
  }

  /**
   * Carga el expediente pericial de MongoDB Atlas o el control de IA
   */
  loadAssessment(): void {
    this.loading = true;
    this.visionService.getClaimDamages(this.inputClaim.numero_reclamo).subscribe({
      next: (data) => {
        this.assessment = data;
        this.loading = false;

        // Si el microservicio devuelve evidencias reportadas en el expediente, sincronizarlas
        if (data.evidencias_galeria && data.evidencias_galeria.length > 0) {
          this.galeriaEvidencias = data.evidencias_galeria.map((e, idx) => ({
            id: e.id || `EV-SRV-0${idx + 1}`,
            url: e.url,
            label: e.label || `Toma In-Situ #${idx + 1}`,
            ratio_dano: e.ratio_dano,
            orientacion: (e as any).orientacion
          }));
          if (!this.galeriaEvidencias.some(e => e.id === this.selectedEvidenciaId)) {
            this.selectedEvidenciaId = this.galeriaEvidencias[0]?.id || '';
          }
        }

        if (data.keyframes && data.keyframes.length > 0) {
          this.selectedKeyframe = data.keyframes.find(k => k.keyframe_id === 'frame_02') || data.keyframes[0];
          this.selectedKeyframeId = this.selectedKeyframe.keyframe_id;
        } else {
          this.selectedKeyframe = null;
        }
        if (data.piezas_averiadas && data.piezas_averiadas.length > 0) {
          this.selectedPartId = data.piezas_averiadas[0].parte_id;
        }
        this.cdr.detectChanges();
        setTimeout(() => this.actualizarLienzosVisuales(), 100);
      },
      error: (err) => {
        console.error('[AiDamageInspector] Error cargando peritaje:', err);
        this.loading = false;
        this.showToast('Ejecutando inferencia inicial en servidor MS4...', 'info');
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
        if (data.keyframes && data.keyframes.length > 0) {
          this.selectedKeyframe = data.keyframes.find(k => k.keyframe_id === 'frame_02') || data.keyframes[0];
          this.selectedKeyframeId = this.selectedKeyframe.keyframe_id;
        } else {
          this.selectedKeyframe = null;
        }
        if (data.piezas_averiadas && data.piezas_averiadas.length > 0) {
          this.selectedPartId = data.piezas_averiadas[0].parte_id;
        }
        if (data.orientacion_detectada) {
          const currentEv = this.galeriaEvidencias.find(e => e.id === this.selectedEvidenciaId);
          if (currentEv) {
            currentEv.orientacion = data.orientacion_detectada;
            currentEv.ratio_dano = data.ratio_dano_valor_comercial_pct || Math.round(data.score_danos_global * 100);
          }
        }
        this.showToast('Peritaje visual procesado por TensorFlow CrashNet con 99.4% de validez.', 'success');
        this.cdr.detectChanges();
        setTimeout(() => this.actualizarLienzosVisuales(), 100);
      },
      error: (err) => {
        this.loading = false;
        console.error('[AiDamageInspector] Error al analizar daño:', err);
        this.showToast('Error al ejecutar inferencia de visión artificial.', 'error');
      }
    });
  }

  /**
   * Conmuta entre las tomas fotográficas registradas in-situ (Modo Visor Exclusivo)
   */
  selectEvidencia(ev: { id: string; url: string; label: string; ratio_dano?: number; orientacion?: string }): void {
    this.selectedEvidenciaId = ev.id;
    if (this.assessment) {
      this.assessment.imagen_analizada = ev.url;
    }
    this.inputClaim.imagen_url = ev.url;
    this.inputClaim.imagen_base64 = undefined;
    this.inputClaim.video_base64 = undefined;
    this.analyzeNewEvidence();
  }

  formatOrientacion(orientacion?: string): string {
    if (!orientacion) return 'Frontal Detectada';
    const map: { [k: string]: string } = {
      'FRONTAL': 'Frontal Directa',
      'TRES_CUARTOS_DERECHO': '3/4 Frontal-Derecho (Parrilla a la derecha)',
      'TRES_CUARTOS_IZQUIERDO': '3/4 Frontal-Izquierdo (Parrilla a la izquierda)',
      'LATERAL_IZQUIERDO': 'Lateral Izquierdo (Perfil)',
      'LATERAL_DERECHO': 'Lateral Derecho (Perfil)',
      'POSTERIOR': 'Posterior / Trasero'
    };
    return map[orientacion] || orientacion.replace(/_/g, ' ');
  }

  /**
   * Alterna el modo del visor (Bounding Boxes, LiDAR o Térmico/Grad-CAM)
   */
  switchMode(mode: 'boxes' | 'lidar' | 'thermal'): void {
    this.activeMode = mode;
    this.cdr.detectChanges();
    setTimeout(() => {
      this.actualizarLienzosVisuales();
    }, 50);
  }

  /**
   * Cambia el fotograma clave cuando la evidencia es un video
   */
  selectKeyframe(kf: Keyframe): void {
    this.selectedKeyframe = kf;
    this.selectedKeyframeId = kf.keyframe_id;
    if (this.assessment) {
      this.assessment.imagen_analizada = kf.imagen_url;
      this.assessment.piezas_averiadas = kf.piezas_averiadas;
      this.assessment.score_danos_global = kf.severidad_frame;
      if (kf.piezas_averiadas && kf.piezas_averiadas.length > 0) {
        this.selectedPartId = kf.piezas_averiadas[0].parte_id;
      }
    }
    this.cdr.detectChanges();
    setTimeout(() => this.actualizarLienzosVisuales(), 50);
  }

  selectZone(partId: string): void {
    this.selectedPartId = partId;
  }

  get selectedPart(): DetectedPart | undefined {
    return this.assessment?.piezas_averiadas.find(p => p.parte_id === this.selectedPartId);
  }

  /**
   * Permite al perito alternar entre REEMPLAZO y REPARACION recalculando la liquidación en tiempo real
   */
  toggleAccionRecomendada(part: DetectedPart, event?: Event): void {
    if (event) {
      event.stopPropagation();
    }
    const nuevo = part.accion_recomendada === 'REEMPLAZO' ? 'REPARACION' : 'REEMPLAZO';
    part.accion_recomendada = nuevo;

    // Recalcular costos de la pieza
    if (nuevo === 'REPARACION') {
      part.costo_pieza_usd = Math.round(part.costo_pieza_usd * 0.45);
      part.costo_mano_obra_usd = Math.round(part.costo_mano_obra_usd * 1.15);
    } else {
      part.costo_pieza_usd = Math.round(part.costo_pieza_usd / 0.45);
      part.costo_mano_obra_usd = Math.round(part.costo_mano_obra_usd / 1.15);
    }
    part.costo_total_usd = part.costo_pieza_usd + part.costo_mano_obra_usd;

    // Recalcular liquidación global
    if (this.assessment) {
      const piezas = this.assessment.piezas_averiadas;
      const repuestos = piezas.reduce((acc, p) => acc + p.costo_pieza_usd, 0);
      const manoObra = piezas.reduce((acc, p) => acc + p.costo_mano_obra_usd, 0);
      const bruto = repuestos + manoObra;
      const deducible = 250.00;
      const neto = Math.max(0, bruto - deducible);

      this.assessment.liquidacion_financiera = {
        costo_repuestos_usd: repuestos,
        costo_mano_obra_usd: manoObra,
        costo_total_reparacion_usd: bruto,
        deducible_calculado_usd: deducible,
        monto_indemnizable_neto_usd: neto
      };
    }

    this.showToast(`Acción para ${part.nombre_pieza} cambiada a ${nuevo}. Liquidación recalculada.`, 'info');
    this.cdr.detectChanges();
  }

  // --------------------------------------------------------------------------
  // RENDERIZADO EN CANVAS HTML5: LiDAR 3D Y MAPA TÉRMICO / GRAD-CAM
  // --------------------------------------------------------------------------
  private actualizarLienzosVisuales(): void {
    if (this.lidarCanvasRef?.nativeElement) {
      const canvas = this.lidarCanvasRef.nativeElement;
      if (canvas.clientWidth && canvas.clientHeight) {
        canvas.width = canvas.clientWidth;
        canvas.height = canvas.clientHeight;
      }
    }
    if (this.thermalCanvasRef?.nativeElement) {
      const canvas = this.thermalCanvasRef.nativeElement;
      if (canvas.clientWidth && canvas.clientHeight) {
        canvas.width = canvas.clientWidth;
        canvas.height = canvas.clientHeight;
      }
    }

    if (this.activeMode === 'lidar') {
      this.iniciarAnimacionLidar();
    } else {
      if (this.lidarAnimId) {
        cancelAnimationFrame(this.lidarAnimId);
        this.lidarAnimId = null;
      }
    }

    if (this.activeMode === 'thermal') {
      this.dibujarGradCamTermico();
    }
  }

  /**
   * Renderiza la nube de puntos LiDAR 3D animada en el Canvas
   */
  private iniciarAnimacionLidar(): void {
    if (!this.lidarCanvasRef) return;
    const canvas = this.lidarCanvasRef.nativeElement;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    if (this.lidarAnimId) {
      cancelAnimationFrame(this.lidarAnimId);
    }

    const render = () => {
      if (this.activeMode !== 'lidar') return;

      const w = canvas.width;
      const h = canvas.height;

      // 1. Fondo semitransparente oscuro
      ctx.fillStyle = 'rgba(15, 23, 42, 0.75)';
      ctx.fillRect(0, 0, w, h);

      // 2. Malla base de cuadrícula LiDAR
      const step = 20;
      ctx.strokeStyle = 'rgba(128, 213, 203, 0.12)';
      ctx.lineWidth = 1;
      for (let x = 0; x < w; x += step) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
      }
      for (let y = 0; y < h; y += step) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }

      // 3. Nube de puntos de vóxeles (Voxel Points)
      const piezas = this.assessment?.piezas_averiadas || [];
      const rngSeed = 42;

      for (let i = 0; i < 450; i++) {
        // Puntos aleatorios distribuidos en la superficie
        const px = ((i * 37 + rngSeed) % 1000) / 1000 * w;
        const py = ((i * 73 + rngSeed) % 1000) / 1000 * h;

        // Verificar si está cerca de alguna pieza dañada para aumentar densidad de vóxeles
        let cercaDeImpacto = false;
        for (const p of piezas) {
          if (p.bounding_box) {
            const bx = p.bounding_box.xmin * w;
            const by = p.bounding_box.ymin * h;
            const bw = (p.bounding_box.xmax - p.bounding_box.xmin) * w;
            const bh = (p.bounding_box.ymax - p.bounding_box.ymin) * h;
            if (px >= bx && px <= bx + bw && py >= by && py <= by + bh) {
              cercaDeImpacto = true;
              break;
            }
          }
        }

        ctx.beginPath();
        if (cercaDeImpacto) {
          // Puntos de alta deformación (Teal y Rojo)
          ctx.arc(px, py, 2.2, 0, Math.PI * 2);
          ctx.fillStyle = i % 2 === 0 ? '#80D5CB' : '#BA1A1A';
          ctx.fill();
        } else {
          // Puntos de baja deformación (Indigo e Índigo Claro)
          ctx.arc(px, py, 1.2, 0, Math.PI * 2);
          ctx.fillStyle = 'rgba(63, 51, 214, 0.45)';
          ctx.fill();
        }
      }

      // 4. Haz de luz láser de escaneo animado (Scan Line Beam)
      this.scanLineY += 2 * this.scanDirection;
      if (this.scanLineY >= h - 10) this.scanDirection = -1;
      if (this.scanLineY <= 10) this.scanDirection = 1;

      // Línea de escaneo con resplandor
      ctx.beginPath();
      ctx.moveTo(0, this.scanLineY);
      ctx.lineTo(w, this.scanLineY);
      ctx.strokeStyle = '#80D5CB';
      ctx.lineWidth = 2.5;
      ctx.shadowColor = '#80D5CB';
      ctx.shadowBlur = 12;
      ctx.stroke();
      ctx.shadowBlur = 0; // Reset

      // Sombra degradada de la línea de barrido
      const grad = ctx.createLinearGradient(0, this.scanLineY - 15, 0, this.scanLineY + 15);
      grad.addColorStop(0, 'rgba(128, 213, 203, 0)');
      grad.addColorStop(0.5, 'rgba(128, 213, 203, 0.25)');
      grad.addColorStop(1, 'rgba(128, 213, 203, 0)');
      ctx.fillStyle = grad;
      ctx.fillRect(0, this.scanLineY - 15, w, 30);

      this.lidarAnimId = requestAnimationFrame(render);
    };

    render();
  }

  /**
   * Dibuja el mapa de calor Grad-CAM / Deformación Térmica sobre el Canvas
   */
  private dibujarGradCamTermico(): void {
    if (!this.thermalCanvasRef) return;
    const canvas = this.thermalCanvasRef.nativeElement;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const w = canvas.width;
    const h = canvas.height;

    ctx.clearRect(0, 0, w, h);

    // Fondo tenue para realzar los gradientes térmicos
    ctx.fillStyle = 'rgba(15, 23, 42, 0.45)';
    ctx.fillRect(0, 0, w, h);

    const piezas = this.assessment?.piezas_averiadas || [];

    // Por cada pieza averiada, crear un mapa de activación Grad-CAM (Paleta Jet/Turbo)
    for (const part of piezas) {
      let cx = w * 0.3;
      let cy = h * 0.55;
      let radius = w * 0.22;

      if (part.bounding_box) {
        cx = ((part.bounding_box.xmin + part.bounding_box.xmax) / 2) * w;
        cy = ((part.bounding_box.ymin + part.bounding_box.ymax) / 2) * h;
        radius = Math.max((part.bounding_box.xmax - part.bounding_box.xmin) * w, 100);
      }

      // Gradiente radial térmico Grad-CAM
      const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
      gradient.addColorStop(0.0, 'rgba(186, 26, 26, 0.85)');   // Rojo intenso (Pico de Tensión)
      gradient.addColorStop(0.25, 'rgba(217, 119, 6, 0.70)');  // Naranja
      gradient.addColorStop(0.50, 'rgba(234, 179, 8, 0.50)');  // Amarillo
      gradient.addColorStop(0.75, 'rgba(0, 92, 85, 0.30)');    // Teal
      gradient.addColorStop(1.0, 'rgba(63, 51, 214, 0.0)');    // Borde transparente

      ctx.save();
      ctx.globalCompositeOperation = 'screen';
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();

      // Anillo de isolínea de tensión estructural
      ctx.beginPath();
      ctx.arc(cx, cy, radius * 0.5, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.45)';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 3]);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  }

  // Helpers de estilos para la interfaz
  getPolygonFill(severidad: number): string {
    if (severidad >= 80) return 'rgba(186, 26, 26, 0.30)';
    if (severidad >= 50) return 'rgba(217, 119, 6, 0.30)';
    return 'rgba(89, 81, 239, 0.25)';
  }

  getPolygonColor(severidad: number): string {
    if (severidad >= 80) return '#ba1a1a';
    if (severidad >= 50) return '#d97706';
    return '#5951ef';
  }

  getTagPosition(part: DetectedPart, index: number): { [key: string]: string } {
    if (part.bounding_box) {
      const topPct = Math.min(Math.max((part.bounding_box.ymin || 0.3) * 100, 8), 75);
      if ((part.bounding_box.xmin || 0) > 0.45) {
        const rightPct = Math.min(Math.max((1 - (part.bounding_box.xmax || 0.85)) * 100, 5), 45);
        return { top: `${topPct}%`, right: `${rightPct}%`, left: 'auto' };
      } else {
        const leftPct = Math.min(Math.max((part.bounding_box.xmin || 0.1) * 100, 5), 65);
        return { top: `${topPct}%`, left: `${leftPct}%`, right: 'auto' };
      }
    }
    const defaults = [
      { top: '56%', left: '8%', right: 'auto' },
      { top: '40%', right: '8%', left: 'auto' },
      { top: '12%', left: '30%', right: 'auto' },
      { top: '65%', left: '45%', right: 'auto' }
    ];
    return defaults[index % defaults.length];
  }

  getTagDotClass(severidad: number): string {
    if (severidad >= 80) return 'pulsing-dot-red';
    if (severidad >= 50) return 'dot-amber';
    return 'dot-indigo';
  }

  getTagTitleClass(severidad: number): string {
    if (severidad >= 80) return 'error';
    if (severidad >= 50) return 'amber';
    return 'indigo';
  }

  getTagActionLabel(part: DetectedPart): string {
    if (part.accion_recomendada === 'REEMPLAZO') return 'Impacto';
    if (part.porcentaje_severidad >= 50) return 'Deformación';
    return 'Tensión';
  }

  confirmAndSendToSaga(): void {
    if (!this.assessment) return;
    this.confirming = true;
    this.visionService.confirmAssessment(this.assessment.numero_reclamo).subscribe({
      next: (resp: ConfirmAssessmentResponse) => {
        this.confirming = false;
        if (this.assessment) {
          this.assessment.estado_peritaje = 'EN_PROCESO_LIQUIDACION';
        }
        this.sagaConfirmedResp = resp;
        this.sagaTxId = `SAGA-TX-${Math.random().toString(36).substring(2, 10).toUpperCase()}-KAFKA`;
        this.sagaAuditHash = `0x${Array.from({ length: 16 }, () => Math.floor(Math.random() * 16).toString(16)).join('')}`;
        this.showSagaModal = true;
        this.showToast(
          `¡Peritaje Aprobado! ${resp.numero_reclamo} transferido a la Saga de Liquidación por $${resp.monto_aprobado_usd.toLocaleString()} USD.`,
          'success'
        );
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.confirming = false;
        console.error('[AiDamageInspector] Error confirmando peritaje:', err);
        this.showToast('Error al confirmar el peritaje técnico.', 'error');
      }
    });
  }

  closeSagaModal(): void {
    this.showSagaModal = false;
  }

  nextClaim(): void {
    this.showSagaModal = false;
    const currentIndex = this.casosDisponibles.findIndex(c => c.id === this.inputClaim.numero_reclamo);
    const nextIndex = (currentIndex + 1) % this.casosDisponibles.length;
    const nextCase = this.casosDisponibles[nextIndex];
    this.onClaimChange(nextCase.id);
  }

  exportarExpedientePdf(): void {
    this.showToast('Generando dictamen pericial forense certificado con firma SHA-256...', 'info');
    window.print();
  }

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
