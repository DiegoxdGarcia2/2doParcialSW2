import { Component, OnInit, OnDestroy, ChangeDetectorRef, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Chart, registerables } from 'chart.js';
import { VoiceMcpService } from '../../core/services/voice-mcp.service';
import { 
  VoiceMcpResponse, 
  McpToolDefinition, 
  OwaspSecurityAudit, 
  VoiceDeliveryFormat,
  QuickExportRequest 
} from '../../core/models/voice-mcp.models';

Chart.register(...registerables);

@Component({
  selector: 'app-voice-mcp-reports',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './voice-mcp-reports.component.html',
  styleUrls: ['./voice-mcp-reports.component.css']
})
export class VoiceMcpReportsComponent implements OnInit, OnDestroy {
  @ViewChild('audioCanvas', { static: false }) audioCanvas!: ElementRef<HTMLCanvasElement>;
  @ViewChild('contextualChartCanvas', { static: false }) contextualChartCanvasRef!: ElementRef<HTMLCanvasElement>;

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

  // Estado del Formulario, Formatos Cuádruples y Prioridad al Usuario
  promptDictado = '';
  herramientaDetectada = 'tool_reporte_ventas_primas';
  formatoDetectado: VoiceDeliveryFormat = 'pantalla';
  formatoModoManual = false; // true cuando el usuario fijó manualmente el formato
  formatoRazon = 'Vista en pantalla interactiva';

  // Búsqueda y Gráfico Contextual en Pantalla
  busquedaFiltro = '';
  contextualChartInstance: Chart | null = null;
  isExportingHot = false;

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

  // Sugerencias dinámicas en lenguaje natural
  sugerenciasVoz = [
    {
      titulo: 'Demanda de Vehículos en Pantalla',
      frase: 'demanda de vehículos ordenadas por tipo de vehículo del año en curso para ver en pantalla',
      icono: 'desktop_windows',
      formato: 'pantalla' as VoiceDeliveryFormat,
      tag: 'Pantalla'
    },
    {
      titulo: 'Demanda de Vehículos en PDF',
      frase: 'demanda de vehículos ordenadas por tipo de vehículo del año en curso en pdf',
      icono: 'picture_as_pdf',
      formato: 'pdf' as VoiceDeliveryFormat,
      tag: 'PDF (.pdf)'
    },
    {
      titulo: 'Auditoría Forense SIU en Word',
      frase: 'Auditoría forense de talleres con sobreprecios y anomalías en word',
      icono: 'description',
      formato: 'docx' as VoiceDeliveryFormat,
      tag: 'Word (.docx)'
    },
    {
      titulo: 'Solvencia & Reservas en Excel',
      frase: 'Evaluar solvencia técnica Solvency II y ratio de cobertura de reservas en excel',
      icono: 'table_chart',
      formato: 'xlsx' as VoiceDeliveryFormat,
      tag: 'Excel (.xlsx)'
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
    if (this.contextualChartInstance) {
      this.contextualChartInstance.destroy();
      this.contextualChartInstance = null;
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
  // Inferencia Dinámica de Herramienta MCP y Formato
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

    // 2. Detección de Formato (Solo si el usuario NO ha fijado manualmente un formato)
    if (!this.formatoModoManual) {
      if (p.includes('pantalla') || p.includes('ver en pantalla') || p.includes('en pantalla')) {
        this.formatoDetectado = 'pantalla';
        this.formatoRazon = 'Comando exacto de voz: Visualizar en Pantalla';
      } else if (p.includes('excel') || p.includes('xlsx')) {
        this.formatoDetectado = 'xlsx';
        this.formatoRazon = 'Comando exacto de voz: Planilla Excel';
      } else if (p.includes('word') || p.includes('docx')) {
        this.formatoDetectado = 'docx';
        this.formatoRazon = 'Comando exacto de voz: Documento Word';
      } else if (p.includes('pdf')) {
        this.formatoDetectado = 'pdf';
        this.formatoRazon = 'Comando exacto de voz: Certificado PDF';
      } else {
        // Inferencia Autónoma por Dominio de Negocio (Auto-IA)
        if (this.herramientaDetectada === 'tool_reporte_ventas_primas') {
          this.formatoDetectado = 'pantalla';
          this.formatoRazon = 'Auto-IA: Visualización en pantalla con desglose por vehículo';
        } else if (this.herramientaDetectada === 'tool_solvencia_reservas') {
          this.formatoDetectado = 'xlsx';
          this.formatoRazon = 'Auto-IA: Balances numéricos y ratios Solvency II';
        } else if (this.herramientaDetectada === 'tool_reporte_auditoria_fraude_siu') {
          this.formatoDetectado = 'docx';
          this.formatoRazon = 'Auto-IA: Dossier forense de auditoría legal';
        } else {
          this.formatoDetectado = 'pdf';
          this.formatoRazon = 'Auto-IA: Certificado pericial oficial';
        }
      }
    }
  }

  // --------------------------------------------------------------------------
  // Selección Manual de Formato (Prioridad Absoluta al Usuario)
  // --------------------------------------------------------------------------
  cambiarFormatoManual(fmt: VoiceDeliveryFormat): void {
    this.formatoDetectado = fmt;
    this.formatoModoManual = true;
    this.formatoRazon = `Fijado manualmente por el usuario (${this.getFormatLabel(fmt)})`;
  }

  restaurarModoAutoIA(): void {
    this.formatoModoManual = false;
    this.autoAjustarHerramientaYFormato(this.promptDictado);
  }

  getFormatLabel(fmt: string): string {
    switch (fmt) {
      case 'pantalla': return 'Visualizar en Pantalla';
      case 'xlsx': return 'Excel (.xlsx)';
      case 'docx': return 'Word (.docx)';
      case 'pdf': return 'PDF (.pdf)';
      default: return fmt?.toUpperCase() || 'AUTO';
    }
  }

  getFormatIcon(fmt: string): string {
    switch (fmt) {
      case 'pantalla': return 'desktop_windows';
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
        return 'Inferencia Automática (IA / MCP)';
    }
  }

  // --------------------------------------------------------------------------
  // Manejo de Micrófono & Detección de Silencio
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

    this.cuentaRegresivaEnvio = 3;
    this.countdownInterval = setInterval(() => {
      if (this.cuentaRegresivaEnvio > 1) {
        this.cuentaRegresivaEnvio--;
      } else {
        clearInterval(this.countdownInterval);
      }
      this.cdr.detectChanges();
    }, 800);

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

      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const source = this.audioContext.createMediaStreamSource(stream);
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      source.connect(this.analyser);
      this.dibujarOndaAudio();

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
            if (errCode === 'aborted' || errCode === 'no-speech') return;
            console.warn(`[VoiceMCP] SpeechRecognizer (${errCode}):`, e.message || e);
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
      ctx.strokeStyle = '#005C55';
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
  // Ejecución de Comandos MCP & Exportación Dual Inteligente
  // --------------------------------------------------------------------------
  ejecutarComando(): void {
    if (!this.promptDictado && !this.audioBlob) return;

    // Solo reajustar formato si no está fijado manualmente por el usuario
    if (!this.formatoModoManual && this.promptDictado) {
      this.autoAjustarHerramientaYFormato(this.promptDictado);
    }

    this.isLoading = true;
    this.owaspBlockedAlert = null;
    this.lastResponse = null;

    this.voiceService.procesarComandoVoz(
      this.audioBlob || undefined,
      this.promptDictado || undefined,
      this.formatoDetectado,
      undefined
    ).subscribe({
      next: (resp) => {
        this.isLoading = false;
        this.lastResponse = resp;
        this.audioBlob = null;
        this.busquedaFiltro = '';
        if (resp.traza_mcp?.tool_name) {
          this.herramientaDetectada = resp.traza_mcp.tool_name;
        }
        if (!this.formatoModoManual && resp.formato_solicitado) {
          this.formatoDetectado = resp.formato_solicitado as any;
        }
        this.cdr.detectChanges();
        setTimeout(() => {
          this.renderContextualChart();
          if (this.formatoDetectado === 'pantalla') {
            this.desplazarAPanelReporte();
          }
        }, 150);
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

  exportarEnCaliente(formato: 'xlsx' | 'pdf' | 'docx'): void {
    if (!this.lastResponse || !this.lastResponse.filas || this.lastResponse.filas.length === 0) return;

    this.isExportingHot = true;
    const toolName = this.lastResponse.traza_mcp?.tool_name || 'reporte_generativo';

    const payload: QuickExportRequest = {
      titulo: `Reporte ${this.obtenerNombreHerramienta(toolName)}`,
      kpis: this.lastResponse.kpis_resumen || {},
      columnas: this.lastResponse.columnas || [],
      filas: this.lastResponse.filas || [],
      formato: formato,
      nombre_base: toolName.replace('tool_', 'reporte_'),
      params: this.lastResponse.traza_mcp?.arguments
    };

    this.voiceService.exportarDocumentoEnCaliente(payload).subscribe({
      next: (doc) => {
        this.isExportingHot = false;
        if (this.lastResponse) {
          this.lastResponse.documento = doc;
          this.lastResponse.formato_solicitado = formato;
        }
        this.cdr.detectChanges();

        // Disparar descarga en el navegador
        const link = document.createElement('a');
        link.href = doc.download_url.startsWith('http') 
          ? doc.download_url 
          : this.obtenerDownloadUrl(doc.filename);
        link.download = doc.filename;
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      },
      error: (err) => {
        this.isExportingHot = false;
        console.error('Error en exportación en caliente:', err);
        this.cdr.detectChanges();
      }
    });
  }

  get filasFiltradas(): Record<string, any>[] {
    const filas = this.lastResponse?.filas || [];
    if (!this.busquedaFiltro || !this.busquedaFiltro.trim()) {
      return filas;
    }
    const term = this.busquedaFiltro.toLowerCase().trim();
    return filas.filter(f => 
      Object.values(f).some(val => String(val || '').toLowerCase().includes(term))
    );
  }

  desplazarAPanelReporte(): void {
    const el = document.getElementById('panelReporteInteractivo');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  // --------------------------------------------------------------------------
  // Gráfico Contextual Dinámico Chart.js
  // --------------------------------------------------------------------------
  private renderContextualChart(intentos = 0): void {
    if (!this.lastResponse?.filas || this.lastResponse.filas.length === 0) {
      return;
    }

    const canvas = this.contextualChartCanvasRef?.nativeElement || (document.getElementById('contextualChartCanvas') as HTMLCanvasElement);
    if (!canvas) {
      if (intentos < 4) {
        setTimeout(() => this.renderContextualChart(intentos + 1), 120);
      }
      return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    if (this.contextualChartInstance) {
      this.contextualChartInstance.destroy();
      this.contextualChartInstance = null;
    }

    const tool = this.lastResponse.traza_mcp?.tool_name || '';
    const filas = this.lastResponse.filas;

    let chartType: any = 'bar';
    let labels: string[] = [];
    let datasets: any[] = [];
    let scalesConfig: any = {
      x: {
        grid: { display: false },
        ticks: { font: { family: 'JetBrains Mono', size: 11 }, color: '#0F172A' }
      },
      y: {
        grid: { color: '#E2E8F0' },
        ticks: { font: { family: 'JetBrains Mono', size: 10 } }
      }
    };

    if (tool === 'tool_reporte_ventas_primas') {
      labels = filas.map(f => String(f['tipo_vehiculo'] || ''));
      datasets = [
        {
          label: 'Demanda de Pólizas (U)',
          data: filas.map(f => Number(f['demanda_polizas'] || 0)),
          backgroundColor: '#005C55',
          borderRadius: 6,
          yAxisID: 'y'
        },
        {
          label: 'Prima Promedio ($ USD)',
          data: filas.map(f => Number(f['prima_promedio_usd'] || 0)),
          backgroundColor: '#4F46E5',
          borderRadius: 6,
          yAxisID: 'y1'
        }
      ];
      scalesConfig = {
        x: {
          grid: { display: false },
          ticks: { font: { family: 'JetBrains Mono', size: 11 }, color: '#0F172A' }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: { display: true, text: 'Demanda (Pólizas)', font: { size: 10, family: 'Inter' }, color: '#005C55' },
          grid: { color: '#E2E8F0' },
          ticks: { font: { family: 'JetBrains Mono', size: 10 } }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: { display: true, text: 'Prima Promedio ($ USD)', font: { size: 10, family: 'Inter' }, color: '#4F46E5' },
          grid: { drawOnChartArea: false },
          ticks: { 
            font: { family: 'JetBrains Mono', size: 10 },
            callback: (val: any) => `$${val}`
          }
        }
      };
    } else if (tool === 'tool_reporte_siniestralidad') {
      labels = filas.slice(0, 10).map(f => String(f['numero_reclamo'] || f['poliza'] || ''));
      datasets = [
        {
          label: 'Costo Estimado ($ USD)',
          data: filas.slice(0, 10).map(f => Number(f['costo_estimado'] || f['costo_total_usd'] || 0)),
          backgroundColor: '#EF4444',
          borderRadius: 6
        }
      ];
    } else if (tool === 'tool_reporte_auditoria_fraude_siu') {
      labels = filas.slice(0, 10).map(f => String(f['taller_mecanico'] || f['reclamo_id'] || ''));
      datasets = [
        {
          label: 'Score Anomalía (Isolation Forest)',
          data: filas.slice(0, 10).map(f => Number(f['score_anomalia'] || 0)),
          backgroundColor: filas.slice(0, 10).map(f => Number(f['score_anomalia'] || 0) > 0.6 ? '#DC2626' : '#F59E0B'),
          borderRadius: 6
        }
      ];
    } else if (tool === 'tool_solvencia_reservas') {
      labels = filas.map(f => String(f['concepto'] || f['ramo'] || ''));
      datasets = [
        {
          label: 'Monto ($ USD)',
          data: filas.map(f => Number(f['monto_usd'] || f['reserva_tecnica_usd'] || 0)),
          backgroundColor: '#0F766E',
          borderRadius: 6
        }
      ];
    } else {
      const strCol = this.lastResponse.columnas?.find(c => typeof filas[0][c] === 'string') || 'item';
      const numCol = this.lastResponse.columnas?.find(c => typeof filas[0][c] === 'number') || 'valor';
      labels = filas.slice(0, 8).map(f => String(f[strCol] || ''));
      datasets = [
        {
          label: this.formatColumnHeader(numCol),
          data: filas.slice(0, 8).map(f => Number(f[numCol] || 0)),
          backgroundColor: '#005C55',
          borderRadius: 6
        }
      ];
    }

    try {
      this.contextualChartInstance = new Chart(ctx, {
        type: chartType,
        data: { labels, datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
              labels: {
                font: { family: 'Inter', size: 11 },
                color: '#334155'
              }
            }
          },
          scales: scalesConfig
        }
      });
    } catch (errChart) {
      console.warn('[VoiceMCP] Error al renderizar gráfico Chart.js:', errChart);
    }
  }

  aplicarSugerencia(sug: { frase: string; formato?: VoiceDeliveryFormat }): void {
    this.promptDictado = sug.frase;
    if (sug.formato) {
      this.cambiarFormatoManual(sug.formato);
    }
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
