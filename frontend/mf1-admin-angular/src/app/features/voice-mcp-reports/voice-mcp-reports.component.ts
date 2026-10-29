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
  cuentaRegresivaEnvio = 0;
  private autoSendTimer: any = null;
  private countdownInterval: any = null;
  private readonly AUTO_SEND_DELAY_MS = 2500; // 2.5s de silencio tras dictar para auto-enviar

  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private timerInterval: any = null;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private animationFrameId: number | null = null;
  private speechRecognizer: any = null;

  // Estado del Formulario y Detección Autónoma
  promptDictado = '';
  herramientaDetectada = 'tool_reporte_ventas_primas';
  formatoDetectado: 'xlsx' | 'pdf' | 'docx' = 'xlsx';
  formatoRazon = 'Inferencia: Demanda y métricas tabulares numéricas';

  // Estado de Ejecución
  isLoading = false;
  lastResponse: VoiceMcpResponse | null = null;
  owaspBlockedAlert: { error: string; auditoria: OwaspSecurityAudit; mensaje: string } | null = null;
  catalogoTools: McpToolDefinition[] = [];
  activeTab: 'console' | 'security' | 'tools' = 'console';

  // Vectores de ataque para auditoría de seguridad OWASP
  vectoresAtaque = [
    { label: "Tautología ' OR '1'='1", payload: "Generar reporte de siniestros ' OR '1'='1" },
    { label: "Bypass Stacked Queries ; DROP TABLE", payload: "Reporte de liquidaciones ; DROP TABLE poliza; --" },
    { label: "Inyección UNION SELECT", payload: "Reporte de pólizas UNION SELECT username, password FROM usuarios" },
    { label: "Procedimiento xp_cmdshell", payload: "Consultar reservas técnicas ; EXEC xp_cmdshell('whoami')" },
    { label: "Time-blind Benchmark", payload: "Ver siniestros WHERE 1=1 AND benchmark(10000000, MD5(1))" },
  ];

  // Sugerencias dinámicas en lenguaje natural (demanda, segmentación, etc.)
  sugerenciasVoz = [
    {
      titulo: 'Demanda por Tipo de Vehículo',
      frase: 'demanda de vehículos ordenadas por tipo de vehículo del año en curso',
      icono: 'analytics',
      tag: 'Segmentación'
    },
    {
      titulo: 'Auditoría Forense SIU',
      frase: 'Auditoría forense de talleres con sobreprecios y anomalías en Word',
      icono: 'shield_lock',
      tag: 'Word (.docx)'
    },
    {
      titulo: 'Solvencia & Reservas',
      frase: 'Evaluar solvencia técnica Solvency II y ratio de cobertura de reservas en Excel',
      icono: 'account_balance',
      tag: 'Excel (.xlsx)'
    },
    {
      titulo: 'Siniestros TFLite',
      frase: 'Reporte de siniestros de alta severidad con fotos de peritaje en formato PDF',
      icono: 'minor_crash',
      tag: 'PDF (.pdf)'
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
  // Inferencia Dinámica de Herramienta MCP por Lenguaje Natural
  // --------------------------------------------------------------------------
  onPromptInput(nuevoTexto: string): void {
    this.promptDictado = nuevoTexto;
    this.autoAjustarHerramientaYFormato(this.promptDictado);
  }

  autoAjustarHerramientaYFormato(texto: string): void {
    const p = (texto || '').toLowerCase();

    // 1. Detección Autónoma de Herramienta MCP
    if (
      p.includes('fraude') || p.includes('anomali') || p.includes('siu') ||
      p.includes('sospech') || p.includes('forense') || p.includes('taller') ||
      p.includes('sobreprecio') || p.includes('estafa') || p.includes('inflad') ||
      p.includes('irregular') || p.includes('isolation')
    ) {
      this.herramientaDetectada = 'tool_reporte_auditoria_fraude_siu';
    } else if (
      p.includes('solvenc') || p.includes('reserva') || p.includes('liquidez') ||
      p.includes('capital') || p.includes('cobertura') || p.includes('patrimonio') ||
      p.includes('balance') || p.includes('solvency') || p.includes('fondo')
    ) {
      this.herramientaDetectada = 'tool_solvencia_reservas';
    } else if (
      p.includes('venta') || p.includes('prima') || p.includes('actuarial') ||
      p.includes('demanda') || p.includes('suv') || p.includes('sedan') || 
      p.includes('pickup') || p.includes('camioneta') || p.includes('hatchback') || 
      p.includes('motocicleta') || p.includes('poliza') || p.includes('póliza') || 
      p.includes('vehiculo') || p.includes('vehículo') || p.includes('random forest')
    ) {
      this.herramientaDetectada = 'tool_reporte_ventas_primas';
    } else if (
      p.includes('siniestr') || p.includes('peritaj') || p.includes('choque') ||
      p.includes('reclam') || p.includes('inspecc') || p.includes('accidente') ||
      p.includes('daño') || p.includes('severidad') || p.includes('colis')
    ) {
      this.herramientaDetectada = 'tool_reporte_siniestralidad';
    } else {
      this.herramientaDetectada = 'tool_reporte_ventas_primas';
    }

    // 2. Detección Autónoma y Dinámica del Formato Documental Óptimo
    if (p.includes('excel') || p.includes('xlsx') || p.includes('planilla') || p.includes('hoja de calculo') || p.includes('hoja de cálculo')) {
      this.formatoDetectado = 'xlsx';
      this.formatoRazon = 'Comando explícito: Planilla Excel';
    } else if (p.includes('word') || p.includes('docx') || p.includes('minuta') || p.includes('documento word') || p.includes('dossier')) {
      this.formatoDetectado = 'docx';
      this.formatoRazon = 'Comando explícito: Documento Word';
    } else if (p.includes('pdf') || p.includes('acrobat') || p.includes('imprimible')) {
      this.formatoDetectado = 'pdf';
      this.formatoRazon = 'Comando explícito: Certificado PDF';
    } else {
      // Inferencia por Naturaleza del Dominio de Datos
      if (this.herramientaDetectada === 'tool_reporte_ventas_primas') {
        this.formatoDetectado = 'xlsx';
        this.formatoRazon = 'Inferencia: Demanda y métricas tabulares numéricas';
      } else if (this.herramientaDetectada === 'tool_solvencia_reservas') {
        this.formatoDetectado = 'xlsx';
        this.formatoRazon = 'Inferencia: Balances contables y ratios Solvency II';
      } else if (this.herramientaDetectada === 'tool_reporte_auditoria_fraude_siu') {
        this.formatoDetectado = 'docx';
        this.formatoRazon = 'Inferencia: Dossier forense de auditoría legal';
      } else {
        this.formatoDetectado = 'pdf';
        this.formatoRazon = 'Inferencia: Certificado técnico oficial de peritaje';
      }
    }
  }

  cambiarFormatoManual(fmt: 'xlsx' | 'pdf' | 'docx'): void {
    this.formatoDetectado = fmt;
    this.formatoRazon = 'Ajuste manual del usuario';
  }

  getFormatLabel(fmt: string): string {
    switch (fmt) {
      case 'xlsx': return 'Excel (.xlsx)';
      case 'docx': return 'Word (.docx)';
      case 'pdf': return 'PDF (.pdf)';
      default: return fmt?.toUpperCase() || 'AUTO';
    }
  }

  getFormatIcon(fmt: string): string {
    switch (fmt) {
      case 'xlsx': return 'table_chart';
      case 'docx': return 'description';
      case 'pdf': return 'picture_as_pdf';
      default: return 'draft';
    }
  }

  formatColumnHeader(col: string): string {
    if (!col) return '';
    return col.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  formatCellValue(val: any, col: string): string {
    if (val === null || val === undefined) return '-';
    if (typeof val === 'number') {
      const colLow = col.toLowerCase();
      if (colLow.includes('usd') || colLow.includes('prima') || colLow.includes('costo') || colLow.includes('monto') || colLow.includes('volumen') || colLow.includes('valor')) {
        return `$${val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      }
      return val.toLocaleString('en-US');
    }
    return String(val);
  }

  obtenerNombreHerramienta(toolKey?: string): string {
    switch (toolKey) {
      case 'tool_reporte_auditoria_fraude_siu':
        return 'Auditoría SIU (Isolation Forest)';
      case 'tool_solvencia_reservas':
        return 'Solvencia Técnica & Reservas';
      case 'tool_reporte_ventas_primas':
        return 'Demanda, Ventas & Primas (Random Forest)';
      case 'tool_reporte_siniestralidad':
        return 'Siniestralidad & Peritajes TFLite';
      default:
        return 'Inferencia Automática (IA / NLP)';
    }
  }

  // --------------------------------------------------------------------------
  // Manejo de Micrófono & Detección de Silencio (Auto-Envío Inteligente)
  // --------------------------------------------------------------------------
  async toggleGrabacion(): Promise<void> {
    if (this.isRecording) {
      this.detenerYEnviarComando();
    } else {
      await this.iniciarGrabacion();
    }
  }

  private reiniciarTimerAutoEnvio(): void {
    if (this.autoSendTimer) clearTimeout(this.autoSendTimer);
    if (this.countdownInterval) clearInterval(this.countdownInterval);

    if (!this.isRecording || this.promptDictado.trim().length < 5) {
      this.cuentaRegresivaEnvio = 0;
      return;
    }

    // Cuenta regresiva visual de 3 a 1
    this.cuentaRegresivaEnvio = 3;
    this.countdownInterval = setInterval(() => {
      if (this.cuentaRegresivaEnvio > 1) {
        this.cuentaRegresivaEnvio--;
      } else {
        clearInterval(this.countdownInterval);
      }
      this.cdr.detectChanges();
    }, 800);

    // Si transcurren 2.5 segundos de silencio sin nuevas palabras, auto-enviar
    this.autoSendTimer = setTimeout(() => {
      if (this.isRecording && this.promptDictado.trim().length >= 5) {
        this.detenerYEnviarComando();
      }
    }, this.AUTO_SEND_DELAY_MS);
  }

  async iniciarGrabacion(): Promise<void> {
    try {
      this.audioChunks = [];
      this.audioBlob = null;
      this.cuentaRegresivaEnvio = 0;
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream);

      // Iniciar analizador para osciloscopio
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const source = this.audioContext.createMediaStreamSource(stream);
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      source.connect(this.analyser);
      this.dibujarOndaAudio();

      // Reconocimiento acústico en vivo (Web Speech API)
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        try {
          this.speechRecognizer = new SpeechRecognition();
          this.speechRecognizer.lang = 'es-ES';
          this.speechRecognizer.continuous = true;
          this.speechRecognizer.interimResults = true;
          this.speechRecognizer.onresult = (event: any) => {
            let finalTranscript = '';
            for (let i = 0; i < event.results.length; i++) {
              finalTranscript += event.results[i][0].transcript;
            }
            if (finalTranscript.trim()) {
              this.promptDictado = finalTranscript.trim();
              this.autoAjustarHerramientaYFormato(this.promptDictado);
              this.reiniciarTimerAutoEnvio();
              this.cdr.detectChanges();
            }
          };
          this.speechRecognizer.onerror = (e: any) => {
            const errCode = e?.error || 'desconocido';
            if (errCode === 'aborted' || errCode === 'no-speech') {
              return;
            }
            if (errCode === 'audio-capture') {
              console.warn('[VoiceMCP] Hardware de audio en uso o no disponible para Web Speech.');
              return;
            }
            if (errCode === 'not-allowed') {
              console.warn('[VoiceMCP] Permiso de micrófono denegado en el navegador.');
              return;
            }
            if (errCode === 'network') {
              console.warn('[VoiceMCP] Servicio de reconocimiento de voz de Google no disponible temporalmente.');
              return;
            }
            console.warn(`[VoiceMCP] Estado speechRecognizer (${errCode}):`, e.message || e);
          };
          this.speechRecognizer.onend = () => {
            this.speechRecognizer = null;
          };
          this.speechRecognizer.start();
        } catch (e) {
          console.warn('[VoiceMCP] SpeechRecognition no pudo inicializarse:', e);
        }
      }

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = () => {
        this.audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        stream.getTracks().forEach(track => track.stop());
        if (this.promptDictado) {
          this.autoAjustarHerramientaYFormato(this.promptDictado);
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
      this.cdr.detectChanges();
    }
  }

  detenerGrabacion(): void {
    if (this.autoSendTimer) clearTimeout(this.autoSendTimer);
    if (this.countdownInterval) clearInterval(this.countdownInterval);
    this.cuentaRegresivaEnvio = 0;

    if (this.speechRecognizer) {
      try {
        this.speechRecognizer.abort();
      } catch (_) {}
      this.speechRecognizer = null;
    }
    if (this.mediaRecorder && this.isRecording) {
      try {
        this.mediaRecorder.stop();
      } catch (_) {}
      this.isRecording = false;
      clearInterval(this.timerInterval);
      this.cdr.detectChanges();
    }
  }

  detenerYEnviarComando(): void {
    if (this.autoSendTimer) clearTimeout(this.autoSendTimer);
    if (this.countdownInterval) clearInterval(this.countdownInterval);
    this.cuentaRegresivaEnvio = 0;

    this.detenerGrabacion();
    setTimeout(() => {
      this.ejecutarComando();
    }, 150);
  }

  cancelarGrabacion(): void {
    if (this.autoSendTimer) clearTimeout(this.autoSendTimer);
    if (this.countdownInterval) clearInterval(this.countdownInterval);
    this.cuentaRegresivaEnvio = 0;

    this.detenerGrabacion();
    this.promptDictado = '';
    this.audioBlob = null;
    this.cdr.detectChanges();
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
  // Ejecución Dinámica Autónoma de Comandos MCP
  // --------------------------------------------------------------------------
  ejecutarComando(): void {
    if (!this.promptDictado && !this.audioBlob) return;

    if (this.promptDictado) {
      this.autoAjustarHerramientaYFormato(this.promptDictado);
    }

    this.isLoading = true;
    this.owaspBlockedAlert = null;
    this.lastResponse = null;

    // Herramienta y formato 100% inferidos de forma autónoma por IA / Servidor MCP
    this.voiceService.procesarComandoVoz(
      this.audioBlob || undefined,
      this.promptDictado || undefined,
      this.formatoDetectado,
      undefined // No forzar herramienta: resolución automática por NLP/Whisper
    ).subscribe({
      next: (resp) => {
        this.isLoading = false;
        this.lastResponse = resp;
        this.audioBlob = null;
        if (resp.traza_mcp?.tool_name) {
          this.herramientaDetectada = resp.traza_mcp.tool_name;
        }
        if (resp.formato_solicitado) {
          this.formatoDetectado = resp.formato_solicitado as any;
        }
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

  aplicarSugerencia(sug: { frase: string }): void {
    this.promptDictado = sug.frase;
    this.autoAjustarHerramientaYFormato(this.promptDictado);
    this.ejecutarComando();
  }

  probarAtaqueOwasp(vector: { payload: string }): void {
    this.promptDictado = vector.payload;
    this.ejecutarComando();
  }

  obtenerDownloadUrl(filename: string): string {
    return this.voiceService.getDownloadUrl(filename);
  }
}
