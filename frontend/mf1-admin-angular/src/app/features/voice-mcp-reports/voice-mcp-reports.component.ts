import { Component, OnInit, OnDestroy, ChangeDetectorRef, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { VoiceMcpService } from '../../core/services/voice-mcp.service';
import { VoiceMcpResponse, McpToolDefinition, OwaspSecurityAudit } from '../../core/models/voice-mcp.models';

@Component({
  selector: 'app-voice-mcp-reports',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './voice-mcp-reports.component.html',
  styleUrls: ['./voice-mcp-reports.component.css']
})
export class VoiceMcpReportsComponent implements OnInit, OnDestroy {
  @ViewChild('audioCanvas', { static: false }) audioCanvas!: ElementRef<HTMLCanvasElement>;

  // Estado de Grabación y Audio
  isRecording = false;
  recordingDuration = 0;
  audioBlob: Blob | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private timerInterval: any = null;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private animationFrameId: number | null = null;

  // Estado del Formulario
  promptDictado = '';
  formatoSeleccionado: 'pdf' | 'xlsx' | 'docx' = 'pdf';
  herramientaSugerida = 'tool_reporte_siniestralidad';

  // Estado de Ejecución
  isLoading = false;
  lastResponse: VoiceMcpResponse | null = null;
  owaspBlockedAlert: { error: string; auditoria: OwaspSecurityAudit; mensaje: string } | null = null;
  catalogoTools: McpToolDefinition[] = [];
  activeTab: 'console' | 'security' | 'tools' = 'console';

  // Ataques preconfigurados para demostración de ciberseguridad
  vectoresAtaque = [
    { label: "Tautología ' OR '1'='1", payload: "Generar reporte de siniestros ' OR '1'='1" },
    { label: "Bypass Stacked Queries ; DROP TABLE", payload: "Reporte de liquidaciones ; DROP TABLE poliza; --" },
    { label: "Inyección UNION SELECT", payload: "Reporte de pólizas UNION SELECT username, password FROM usuarios" },
    { label: "Procedimiento xp_cmdshell", payload: "Consultar reservas técnicas ; EXEC xp_cmdshell('whoami')" },
    { label: "Time-blind Benchmark", payload: "Ver siniestros WHERE 1=1 AND benchmark(10000000, MD5(1))" },
  ];

  // Comandos de voz de negocio predefinidos
  comandosVozPresets = [
    {
      titulo: 'Siniestros de Alta Severidad (PDF)',
      comando: 'Generar reporte de siniestros de alta severidad con costos de peritaje en formato PDF',
      formato: 'pdf' as const,
      herramienta: 'tool_reporte_siniestralidad'
    },
    {
      titulo: 'Ventas y Primas SUV (Excel)',
      comando: 'Informe actuarial de primas anuales y proyección de ventas para vehículos SUV en formato Excel',
      formato: 'xlsx' as const,
      herramienta: 'tool_reporte_ventas_primas'
    },
    {
      titulo: 'Auditoría Forense SIU (Word)',
      comando: 'Auditoría de siniestros sospechosos con anomalías detectadas por Isolation Forest en Word',
      formato: 'docx' as const,
      herramienta: 'tool_reporte_auditoria_fraude_siu'
    },
    {
      titulo: 'Solvencia y Reservas (Excel)',
      comando: 'Evaluar solvencia técnica Solvency II y ratio de cobertura de reservas en Excel',
      formato: 'xlsx' as const,
      herramienta: 'tool_solvencia_reservas'
    }
  ];

  constructor(
    private voiceService: VoiceMcpService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.cargarCatalogoTools();
  }

  ngOnDestroy(): void {
    this.detenerGrabacion();
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
    }
  }

  cargarCatalogoTools(): void {
    this.voiceService.obtenerCatalogoTools().subscribe({
      next: (tools) => {
        this.catalogoTools = tools;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.warn('Servidor MCP no disponible o sin conexión:', err);
      }
    });
  }

  // --------------------------------------------------------------------------
  // Manejo de Micrófono & Canvas de Onda de Audio
  // --------------------------------------------------------------------------
  async toggleGrabacion(): Promise<void> {
    if (this.isRecording) {
      this.detenerGrabacion();
    } else {
      await this.iniciarGrabacion();
    }
  }

  async iniciarGrabacion(): Promise<void> {
    try {
      this.audioChunks = [];
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream);

      // Iniciar analizador para osciloscopio
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const source = this.audioContext.createMediaStreamSource(stream);
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      source.connect(this.analyser);
      this.dibujarOndaAudio();

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = () => {
        this.audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        stream.getTracks().forEach(track => track.stop());
        if (!this.promptDictado) {
          this.promptDictado = 'Generar reporte de siniestralidad de alta severidad en formato PDF';
        }
        this.cdr.detectChanges();
      };

      this.mediaRecorder.start();
      this.isRecording = true;
      this.recordingDuration = 0;
      this.timerInterval = setInterval(() => {
        this.recordingDuration++;
        this.cdr.detectChanges();
      }, 1000);
      this.cdr.detectChanges();
    } catch (err) {
      console.error('Error al acceder al micrófono:', err);
      // Fallback a dictado manual
      this.promptDictado = 'Generar reporte de siniestros de alta severidad con peritaje en formato PDF';
      this.cdr.detectChanges();
    }
  }

  detenerGrabacion(): void {
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop();
      this.isRecording = false;
      clearInterval(this.timerInterval);
      this.cdr.detectChanges();
    }
  }

  private dibujarOndaAudio(): void {
    if (!this.audioCanvas || !this.analyser) return;
    const canvas = this.audioCanvas.nativeElement;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const renderFrame = () => {
      this.animationFrameId = requestAnimationFrame(renderFrame);
      if (!this.isRecording) return;

      this.analyser!.getByteTimeDomainData(dataArray);

      ctx.fillStyle = '#0F172A';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.lineWidth = 2.5;
      ctx.strokeStyle = '#005C55'; // Executive Teal
      ctx.beginPath();

      const sliceWidth = canvas.width / bufferLength;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = (v * canvas.height) / 2;

        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
        x += sliceWidth;
      }

      ctx.lineTo(canvas.width, canvas.height / 2);
      ctx.stroke();
    };

    renderFrame();
  }

  // --------------------------------------------------------------------------
  // Ejecución de Comandos & Invocación MCP
  // --------------------------------------------------------------------------
  ejecutarComando(): void {
    if (!this.promptDictado && !this.audioBlob) return;

    this.isLoading = true;
    this.owaspBlockedAlert = null;
    this.lastResponse = null;

    this.voiceService.procesarComandoVoz(
      this.audioBlob || undefined,
      this.promptDictado,
      this.formatoSeleccionado,
      this.herramientaSugerida
    ).subscribe({
      next: (resp) => {
        this.isLoading = false;
        this.lastResponse = resp;
        this.audioBlob = null;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isLoading = false;
        if (err.status === 400 && err.error?.detail) {
          const det = err.error.detail;
          this.owaspBlockedAlert = {
            error: det.error || 'Ataque Bloqueado',
            auditoria: det.auditoria_seguridad || {},
            mensaje: det.mensaje || 'Intento de inyección SQL neutralizado'
          };
        } else {
          console.error('Error al procesar comando:', err);
        }
        this.cdr.detectChanges();
      }
    });
  }

  seleccionarPreset(preset: typeof this.comandosVozPresets[0]): void {
    this.promptDictado = preset.comando;
    this.formatoSeleccionado = preset.formato;
    this.herramientaSugerida = preset.herramienta;
    this.ejecutarComando();
  }

  probarAtaqueOwasp(vector: typeof this.vectoresAtaque[0]): void {
    this.promptDictado = vector.payload;
    this.ejecutarComando();
  }

  obtenerDownloadUrl(filename: string): string {
    return this.voiceService.getDownloadUrl(filename);
  }
}
