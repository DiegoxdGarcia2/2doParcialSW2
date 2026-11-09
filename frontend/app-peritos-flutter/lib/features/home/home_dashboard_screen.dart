import 'dart:convert';
import 'dart:async';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../core/theme/aegis_theme.dart';
import '../../core/config/app_config.dart';
import '../../core/database/database_helper.dart';
import '../../core/utils/file_download_helper.dart';
import '../emergency_sos/sos_emergency_screen.dart';
import '../inspection_peritaje/peritaje_capture_screen.dart';
import '../offline_sync/sync_queue_screen.dart';
import '../saga_tracking/saga_timeline_screen.dart';
import '../qr_payments/qr_payment_screen.dart';

class HomeDashboardScreen extends StatefulWidget {
  const HomeDashboardScreen({super.key});

  @override
  State<HomeDashboardScreen> createState() => _HomeDashboardScreenState();
}

class _HomeDashboardScreenState extends State<HomeDashboardScreen> {
  int _inspeccionesCount = 0;
  int _pendientesSyncCount = 0;
  int _sosCount = 0;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _cargarMetricas();
  }

  Future<void> _cargarMetricas() async {
    final todas = await DatabaseHelper.instance.obtenerTodasInspecciones();
    final pendientes = await DatabaseHelper.instance.obtenerInspeccionesPendientes();
    final sos = await DatabaseHelper.instance.obtenerSosPendientes();

    setState(() {
      _inspeccionesCount = todas.length;
      _pendientesSyncCount = pendientes.length;
      _sosCount = sos.length;
      _isLoading = false;
    });
  }

  void _mostrarConfiguracionIp() {
    final ipController = TextEditingController(text: AppConfig.hostIp);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AegisTheme.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: AegisTheme.surfaceBorder),
        ),
        title: const Text('Configuración de IP Backend', style: TextStyle(color: AegisTheme.textPrimary)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Ajusta la IP del host si estás probando con un teléfono físico por Wi-Fi:',
              style: TextStyle(color: AegisTheme.textSecondary, fontSize: 13),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: ipController,
              decoration: const InputDecoration(
                labelText: 'Host IP (ej. 192.168.1.5 o 10.0.2.2)',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Cancelar', style: TextStyle(color: AegisTheme.textSecondary)),
          ),
          ElevatedButton(
            onPressed: () {
              setState(() {
                AppConfig.hostIp = ipController.text.trim();
              });
              Navigator.of(ctx).pop();
            },
            child: const Text('Guardar'),
          ),
        ],
      ),
    );
  }

  void _mostrarAsistenteVozMcp() {
    final comandoController = TextEditingController(
      text: 'Generar reporte de siniestralidad de alta severidad en formato PDF',
    );
    String formatoSeleccionado = 'pdf';
    bool formatoManual = false;
    bool enviando = false;

    // Estado del HUD Stepper de Cinemática (4 Fases)
    int faseActual = 1;
    String faseTitulo = 'Fase 1: Transcripción Acústica Whisper STT';
    String faseSubtitulo = 'Decodificando ondas de audio y extrayendo entidades actuariales...';
    Timer? hudTimer;

    // Estado de Resultados
    Map<String, dynamic>? documentoGenerado;
    Map<String, dynamic>? kpisResumen;
    List<dynamic>? filasReporte;
    List<dynamic>? columnasReporte;
    String? urlDocumento;
    String? nombreArchivo;
    Map<String, dynamic>? alertaOwasp;

    void autoDetectarFormato(String text, void Function(void Function()) setModalState) {
      if (formatoManual) return;
      final lower = text.toLowerCase();
      String nuevoFormato = formatoSeleccionado;
      if (lower.contains('pantalla') || lower.contains('ver en pantalla')) {
        nuevoFormato = 'pantalla';
      } else if (lower.contains('excel') || lower.contains('xlsx')) {
        nuevoFormato = 'xlsx';
      } else if (lower.contains('word') || lower.contains('docx')) {
        nuevoFormato = 'docx';
      } else if (lower.contains('pdf')) {
        nuevoFormato = 'pdf';
      }
      if (nuevoFormato != formatoSeleccionado) {
        setModalState(() {
          formatoSeleccionado = nuevoFormato;
        });
      }
    }

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AegisTheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => StatefulBuilder(
        builder: (context, setModalState) => Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(context).viewInsets.bottom + 20,
            left: 20,
            right: 20,
            top: 20,
          ),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Cabecera Modal con Badge Ejecutivo
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: AegisTheme.primary.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: const Icon(Icons.mic, color: AegisTheme.primary, size: 22),
                        ),
                        const SizedBox(width: 10),
                        const Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Asistente de Voz MCP (CU15)',
                              style: TextStyle(
                                color: AegisTheme.textPrimary,
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                            Text(
                              'Whisper STT • Anti-SQLi Guard • MS4 Python',
                              style: TextStyle(
                                color: AegisTheme.textSecondary,
                                fontSize: 11,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, color: AegisTheme.textMuted),
                      onPressed: () {
                        hudTimer?.cancel();
                        Navigator.pop(ctx);
                      },
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Comandos Sugeridos Dinámicos
                const Text(
                  'Comandos de voz sugeridos (o edita el texto libremente):',
                  style: TextStyle(color: AegisTheme.textSecondary, fontSize: 11),
                ),
                const SizedBox(height: 8),
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: [
                      ActionChip(
                        avatar: const Icon(Icons.desktop_windows, size: 14, color: Colors.cyanAccent),
                        label: const Text('Demanda (Pantalla)', style: TextStyle(fontSize: 11)),
                        onPressed: () {
                          setModalState(() {
                            formatoManual = true;
                            formatoSeleccionado = 'pantalla';
                            comandoController.text =
                                'Demanda de vehículos ordenados por tipo de vehículo del año en curso para ver en pantalla';
                          });
                        },
                      ),
                      const SizedBox(width: 6),
                      ActionChip(
                        avatar: const Icon(Icons.picture_as_pdf, size: 14, color: AegisTheme.primary),
                        label: const Text('Siniestros (PDF)', style: TextStyle(fontSize: 11)),
                        onPressed: () {
                          setModalState(() {
                            formatoManual = true;
                            formatoSeleccionado = 'pdf';
                            comandoController.text =
                                'Generar reporte de siniestralidad de alta severidad en formato PDF';
                          });
                        },
                      ),
                      const SizedBox(width: 6),
                      ActionChip(
                        avatar: const Icon(Icons.table_chart, size: 14, color: Colors.greenAccent),
                        label: const Text('Ventas y Primas (Excel)', style: TextStyle(fontSize: 11)),
                        onPressed: () {
                          setModalState(() {
                            formatoManual = true;
                            formatoSeleccionado = 'xlsx';
                            comandoController.text =
                                'Generar reporte actuarial de ventas y primas para SUV en formato Excel';
                          });
                        },
                      ),
                      const SizedBox(width: 6),
                      ActionChip(
                        avatar: const Icon(Icons.description, size: 14, color: Colors.lightBlueAccent),
                        label: const Text('Fraude SIU (Word)', style: TextStyle(fontSize: 11)),
                        onPressed: () {
                          setModalState(() {
                            formatoManual = true;
                            formatoSeleccionado = 'docx';
                            comandoController.text =
                                'Auditar sospechas de fraude vehicular con anomalías en Word';
                          });
                        },
                      ),
                      const SizedBox(width: 6),
                      ActionChip(
                        avatar: const Icon(Icons.security, size: 14, color: Colors.redAccent),
                        label: const Text('Ataque SQLi (Blindaje)', style: TextStyle(fontSize: 11, color: Colors.redAccent)),
                        onPressed: () {
                          setModalState(() {
                            formatoManual = true;
                            formatoSeleccionado = 'pdf';
                            comandoController.text =
                                "Dame los siniestros ' OR 1=1 -- UNION SELECT * FROM usuarios";
                          });
                        },
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),

                // Campo de Texto Dictado con Auto-Detección Fluida
                TextField(
                  controller: comandoController,
                  maxLines: 2,
                  onChanged: (text) => autoDetectarFormato(text, setModalState),
                  style: const TextStyle(color: AegisTheme.textPrimary, fontSize: 13),
                  decoration: const InputDecoration(
                    labelText: 'Comando de Voz Dictado (Editable)',
                    hintText: 'Ej. Reporte de siniestros de alta severidad en PDF',
                    prefixIcon: Icon(Icons.record_voice_over, color: AegisTheme.primary),
                  ),
                ),
                const SizedBox(height: 14),

                // Selector Cuádruple de Formatos
                Row(
                  children: [
                    const Text('Formato:', style: TextStyle(color: AegisTheme.textSecondary, fontSize: 13)),
                    const SizedBox(width: 8),
                    ChoiceChip(
                      avatar: const Icon(Icons.desktop_windows, size: 13),
                      label: const Text('Pantalla'),
                      selected: formatoSeleccionado == 'pantalla',
                      onSelected: (val) {
                        setModalState(() {
                          formatoManual = true;
                          formatoSeleccionado = 'pantalla';
                        });
                      },
                    ),
                    const SizedBox(width: 6),
                    ChoiceChip(
                      avatar: const Icon(Icons.picture_as_pdf, size: 13),
                      label: const Text('PDF'),
                      selected: formatoSeleccionado == 'pdf',
                      onSelected: (val) {
                        setModalState(() {
                          formatoManual = true;
                          formatoSeleccionado = 'pdf';
                        });
                      },
                    ),
                    const SizedBox(width: 6),
                    ChoiceChip(
                      avatar: const Icon(Icons.table_chart, size: 13),
                      label: const Text('Excel'),
                      selected: formatoSeleccionado == 'xlsx',
                      onSelected: (val) {
                        setModalState(() {
                          formatoManual = true;
                          formatoSeleccionado = 'xlsx';
                        });
                      },
                    ),
                    const SizedBox(width: 6),
                    ChoiceChip(
                      avatar: const Icon(Icons.description, size: 13),
                      label: const Text('Word'),
                      selected: formatoSeleccionado == 'docx',
                      onSelected: (val) {
                        setModalState(() {
                          formatoManual = true;
                          formatoSeleccionado = 'docx';
                        });
                      },
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // 🎬 HUD Cinemática Animada de 4 Fases (Durante el procesamiento)
                if (enviando)
                  Container(
                    padding: const EdgeInsets.all(14),
                    margin: const EdgeInsets.only(bottom: 14),
                    decoration: BoxDecoration(
                      color: AegisTheme.surfaceElevated,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: AegisTheme.primary.withValues(alpha: 0.4)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2, color: AegisTheme.primary),
                            ),
                            const SizedBox(width: 10),
                            Text(
                              faseTitulo,
                              style: const TextStyle(
                                color: AegisTheme.primary,
                                fontSize: 13,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Text(
                          faseSubtitulo,
                          style: const TextStyle(color: AegisTheme.textSecondary, fontSize: 11),
                        ),
                        const SizedBox(height: 10),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: LinearProgressIndicator(
                            value: faseActual / 4.0,
                            backgroundColor: AegisTheme.surface,
                            valueColor: const AlwaysStoppedAnimation<Color>(AegisTheme.primary),
                            minHeight: 4,
                          ),
                        ),
                      ],
                    ),
                  ),

                // 🛡️ Alerta de Seguridad OWASP (Ataques SQLi Interceptados)
                if (alertaOwasp != null)
                  Container(
                    padding: const EdgeInsets.all(14),
                    margin: const EdgeInsets.only(bottom: 14),
                    decoration: BoxDecoration(
                      color: Colors.red.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: Colors.redAccent.withValues(alpha: 0.6)),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.shield, color: Colors.redAccent, size: 28),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Escudo OWASP: Inyección SQL Neutralizada',
                                style: TextStyle(
                                  color: Colors.redAccent,
                                  fontSize: 13,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                alertaOwasp?['mensaje'] ?? 'Intento de inyección interceptado antes de la base de datos.',
                                style: const TextStyle(color: AegisTheme.textPrimary, fontSize: 12),
                              ),
                              const SizedBox(height: 6),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                decoration: BoxDecoration(
                                  color: Colors.redAccent.withValues(alpha: 0.15),
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Text(
                                  'Regla: ${alertaOwasp?['auditoria_seguridad']?['rule_triggered'] ?? 'Tautología / Stacked Query'} • Nivel 3 Activo',
                                  style: const TextStyle(color: Colors.redAccent, fontSize: 10, fontWeight: FontWeight.w600),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),

                // 📄 Tarjeta Ejecutiva para Reportes Físicos (PDF, Excel, Word con Auto-Descarga)
                if (documentoGenerado != null && formatoSeleccionado != 'pantalla')
                  Container(
                    padding: const EdgeInsets.all(14),
                    margin: const EdgeInsets.only(bottom: 14),
                    decoration: BoxDecoration(
                      color: AegisTheme.surfaceElevated,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: AegisTheme.primary.withValues(alpha: 0.5)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.check_circle, color: AegisTheme.primary, size: 20),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                'Reporte ${formatoSeleccionado.toUpperCase()} generado exitosamente',
                                style: const TextStyle(
                                  color: AegisTheme.textPrimary,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 13,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                          decoration: BoxDecoration(
                            color: AegisTheme.primary.withValues(alpha: 0.12),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: const Row(
                            children: [
                              Icon(Icons.download_done, color: AegisTheme.primary, size: 16),
                              SizedBox(width: 6),
                              Expanded(
                                child: Text(
                                  'Descarga iniciada automáticamente en su navegador',
                                  style: TextStyle(
                                    color: AegisTheme.primary,
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 12),
                        // Botón de Apertura Rápida
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AegisTheme.primary,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 11),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                            ),
                            onPressed: () {
                              if (urlDocumento != null && nombreArchivo != null) {
                                FileDownloadHelper.downloadOrOpen(urlDocumento!, nombreArchivo!);
                              }
                            },
                            icon: const Icon(Icons.open_in_new, size: 16),
                            label: Text('Abrir / Ver Documento (${formatoSeleccionado.toUpperCase()})'),
                          ),
                        ),
                        const SizedBox(height: 8),
                        // Pie Sutil de Seguridad
                        Row(
                          children: [
                            const Icon(Icons.verified, size: 12, color: AegisTheme.textMuted),
                            const SizedBox(width: 4),
                            Text(
                              'SHA-256: ${(documentoGenerado?['sha256_hash'] ?? '').toString().padRight(16).substring(0, 16)}... • Fuente: Neon PostgreSQL',
                              style: const TextStyle(color: AegisTheme.textMuted, fontSize: 10),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),

                // 📊 Visualización En Pantalla Interactiva (KPIs y Tabla de Datos)
                if (formatoSeleccionado == 'pantalla' && filasReporte != null)
                  Container(
                    padding: const EdgeInsets.all(14),
                    margin: const EdgeInsets.only(bottom: 14),
                    decoration: BoxDecoration(
                      color: AegisTheme.surfaceElevated,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: Colors.cyanAccent.withValues(alpha: 0.4)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.table_view, color: Colors.cyanAccent, size: 18),
                            SizedBox(width: 8),
                            Text(
                              'Resumen Ejecutivo en Pantalla',
                              style: TextStyle(
                                color: AegisTheme.textPrimary,
                                fontWeight: FontWeight.bold,
                                fontSize: 13,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        // KPIs en Chips
                        if (kpisResumen != null)
                          Wrap(
                            spacing: 8,
                            runSpacing: 6,
                            children: kpisResumen!.entries.take(4).map((e) {
                              return Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: AegisTheme.surface,
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: AegisTheme.surfaceBorder),
                                ),
                                child: Text(
                                  '${e.key.replaceAll('_', ' ').toUpperCase()}: ${e.value}',
                                  style: const TextStyle(fontSize: 10, color: AegisTheme.textPrimary, fontWeight: FontWeight.w600),
                                ),
                              );
                            }).toList(),
                          ),
                        const SizedBox(height: 12),
                        // Tabla de Registros
                        SingleChildScrollView(
                          scrollDirection: Axis.horizontal,
                          child: DataTable(
                            headingRowHeight: 32,
                            dataRowMinHeight: 28,
                            dataRowMaxHeight: 36,
                            headingTextStyle: const TextStyle(color: Colors.cyanAccent, fontSize: 11, fontWeight: FontWeight.bold),
                            dataTextStyle: const TextStyle(color: AegisTheme.textPrimary, fontSize: 11),
                            columns: (columnasReporte ?? ['Columna'])
                                .map((col) => DataColumn(label: Text(col.toString().toUpperCase())))
                                .toList(),
                            rows: (filasReporte ?? []).take(6).map((fila) {
                              final map = Map<String, dynamic>.from(fila as Map);
                              return DataRow(
                                cells: (columnasReporte ?? []).map((col) {
                                  return DataCell(Text(map[col]?.toString() ?? '-'));
                                }).toList(),
                              );
                            }).toList(),
                          ),
                        ),
                        const SizedBox(height: 6),
                        const Align(
                          alignment: Alignment.centerRight,
                          child: Text(
                            'Fuente: Neon Serverless PostgreSQL (1200 pólizas)',
                            style: TextStyle(fontSize: 10, color: AegisTheme.textMuted),
                          ),
                        ),
                      ],
                    ),
                  ),

                // Botón Principal de Envío
                ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AegisTheme.primary,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 13),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  onPressed: enviando
                      ? null
                      : () async {
                          setModalState(() {
                            enviando = true;
                            faseActual = 1;
                            faseTitulo = 'Fase 1: Transcripción Acústica Whisper STT';
                            faseSubtitulo = 'Decodificando ondas de audio y extrayendo entidades actuariales...';
                            alertaOwasp = null;
                            documentoGenerado = null;
                            filasReporte = null;
                            columnasReporte = null;
                            kpisResumen = null;
                          });

                          // Disparar Cinemática Animada de Fases
                          hudTimer?.cancel();
                          hudTimer = Timer.periodic(const Duration(milliseconds: 320), (timer) {
                            if (faseActual < 4) {
                              setModalState(() {
                                faseActual++;
                                if (faseActual == 2) {
                                  faseTitulo = 'Fase 2: Escudo de Seguridad OWASP Anti-SQLi';
                                  faseSubtitulo = 'Sanitizando tokens y neutralizando inyecciones...';
                                } else if (faseActual == 3) {
                                  faseTitulo = 'Fase 3: Query Builder MCP en PostgreSQL';
                                  faseSubtitulo = 'Consultando base de datos relacional y dataset histórico...';
                                } else if (faseActual == 4) {
                                  faseTitulo = 'Fase 4: Compilación Documental & Almacenamiento S3';
                                  faseSubtitulo = 'Ensamblando documento oficial y firma criptográfica...';
                                }
                              });
                            }
                          });

                          try {
                            final uri = Uri.parse(AppConfig.endpointVoiceMcpCommand);
                            final request = http.MultipartRequest('POST', uri);
                            request.fields['prompt_dictado'] = comandoController.text;
                            request.fields['formato_preferido'] = formatoSeleccionado;

                            final streamedResponse = await request.send().timeout(const Duration(seconds: 12));
                            final response = await http.Response.fromStream(streamedResponse);

                            hudTimer?.cancel();

                            if (response.statusCode == 200) {
                              final data = json.decode(response.body);
                              final doc = data['documento'];
                              final rawUrl = (doc?['download_url'] ?? doc?['local_download_url'] ?? '') as String;
                              final fullUrl = rawUrl.startsWith('http') ? rawUrl : '${AppConfig.ms4BaseUrl}$rawUrl';
                              final fname = (doc?['filename'] ?? 'reporte_$formatoSeleccionado').toString();

                              // ⚡ AUTO-DESCARGA INMEDIATA EN SEGUNDO PLANO PARA FORMATOS FÍSICOS
                              if (formatoSeleccionado != 'pantalla' && fullUrl.isNotEmpty) {
                                FileDownloadHelper.downloadOrOpen(fullUrl, fname);
                              }

                              setModalState(() {
                                documentoGenerado = doc != null ? Map<String, dynamic>.from(doc) : null;
                                kpisResumen = data['kpis_resumen'] != null ? Map<String, dynamic>.from(data['kpis_resumen']) : null;
                                filasReporte = data['filas'] != null ? List<dynamic>.from(data['filas']) : null;
                                columnasReporte = data['columnas'] != null ? List<dynamic>.from(data['columnas']) : null;
                                urlDocumento = fullUrl;
                                nombreArchivo = fname;
                                enviando = false;
                              });
                            } else {
                              final err = json.decode(response.body);
                              setModalState(() {
                                alertaOwasp = err['detail'] is Map ? Map<String, dynamic>.from(err['detail']) : {'mensaje': err['detail']?.toString()};
                                enviando = false;
                              });
                            }
                          } catch (e) {
                            hudTimer?.cancel();
                            setModalState(() {
                              alertaOwasp = {'mensaje': 'Error al conectar con MS4 (Puerto 8004): $e'};
                              enviando = false;
                            });
                          }
                        },
                  icon: enviando
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : const Icon(Icons.auto_awesome),
                  label: Text(enviando ? 'PROCESANDO EN MS4 MCP...' : 'EJECUTAR COMANDO DE VOZ MCP'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: AegisTheme.primary.withOpacity(0.15),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.shield, color: AegisTheme.primary, size: 22),
            ),
            const SizedBox(width: 10),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'AegisCore AI',
                  style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
                ),
                Text(
                  'Peritaje Móvil & Siniestros (Perfil B)',
                  style: TextStyle(fontSize: 11, color: AegisTheme.textSecondary),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_ethernet),
            tooltip: 'Configurar IP Backend',
            onPressed: _mostrarConfiguracionIp,
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() => _isLoading = true);
              _cargarMetricas();
            },
          ),
        ],
        bottom: _isLoading
            ? const PreferredSize(
                preferredSize: Size.fromHeight(2),
                child: LinearProgressIndicator(color: AegisTheme.primary, minHeight: 2),
              )
            : null,
      ),
      body: RefreshIndicator(
        onRefresh: _cargarMetricas,
        color: AegisTheme.primary,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Estado de Conectividad & Backend
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: AegisTheme.glassCardDecoration(borderColor: AegisTheme.primary.withOpacity(0.4)),
                child: Wrap(
                  alignment: WrapAlignment.spaceBetween,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  spacing: 8,
                  runSpacing: 6,
                  children: [
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: const BoxDecoration(
                            color: AegisTheme.success,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Host Backend: ${AppConfig.hostIp}',
                          style: const TextStyle(color: AegisTheme.textPrimary, fontWeight: FontWeight.w600, fontSize: 12),
                        ),
                      ],
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: AegisTheme.surfaceElevated,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: AegisTheme.surfaceBorder),
                      ),
                      child: const Text('MS2: 8002 • MS3: 8003 • MS4: 8004', style: TextStyle(color: AegisTheme.textMuted, fontSize: 10)),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // Métricas de Persistencia Local SQLite
              Row(
                children: [
                  Expanded(
                    child: _buildMetricCard(
                      titulo: 'Inspecciones SQLite',
                      valor: '$_inspeccionesCount',
                      icono: Icons.folder_special,
                      color: AegisTheme.primary,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildMetricCard(
                      titulo: 'Cola Sync DynamoDB',
                      valor: '$_pendientesSyncCount',
                      icono: Icons.cloud_sync,
                      color: _pendientesSyncCount > 0 ? AegisTheme.warning : AegisTheme.success,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildMetricCard(
                      titulo: 'SOS Pendientes',
                      valor: '$_sosCount',
                      icono: Icons.emergency,
                      color: _sosCount > 0 ? AegisTheme.emergency : AegisTheme.textMuted,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 28),

              const Text(
                'MÓDULOS OPERACIONALES (CU06 - CU10)',
                style: TextStyle(
                  color: AegisTheme.textMuted,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),

              const SizedBox(height: 14),

              // 1. CU06: SOS Emergencia
              _buildFeatureCard(
                titulo: 'CU06: Siniestro Emergencia SOS',
                subtitulo: 'Triaje GPS automático, inmovilización y envío directo.',
                icono: Icons.emergency,
                colorIcono: AegisTheme.emergency,
                onTap: () async {
                  await Navigator.push(context, MaterialPageRoute(builder: (_) => const SosEmergencyScreen()));
                  _cargarMetricas();
                },
              ),

              const SizedBox(height: 12),

              // 2. CU07: Peritaje Técnico con Edge AI
              _buildFeatureCard(
                titulo: 'CU07: Peritaje Offline + Edge AI (TFLite)',
                subtitulo: 'Clasificación local de daños en parachoques, capó, puertas y faroles.',
                icono: Icons.precision_manufacturing,
                colorIcono: AegisTheme.primary,
                onTap: () async {
                  await Navigator.push(context, MaterialPageRoute(builder: (_) => const PeritajeCaptureScreen()));
                  _cargarMetricas();
                },
              ),

              const SizedBox(height: 12),

              // 3. CU08: Sincronización Idempotente
              _buildFeatureCard(
                titulo: 'CU08: Sincronización Idempotente DynamoDB',
                subtitulo: 'Cola offline con UUIDv4 y Hash SHA-256 tolerante a intermitencia.',
                icono: Icons.sync_problem_rounded,
                colorIcono: AegisTheme.warning,
                badge: _pendientesSyncCount > 0 ? '$_pendientesSyncCount pendientes' : null,
                onTap: () async {
                  await Navigator.push(context, MaterialPageRoute(builder: (_) => const SyncQueueScreen()));
                  _cargarMetricas();
                },
              ),

              const SizedBox(height: 12),

              // 4. CU09: Orquestación Saga
              _buildFeatureCard(
                titulo: 'CU09: Liquidación Transversal Saga',
                subtitulo: 'Timeline interactivo de la transacción Saga coordinada en 3 MS.',
                icono: Icons.account_tree_rounded,
                colorIcono: AegisTheme.secondary,
                onTap: () {
                  Navigator.push(context, MaterialPageRoute(builder: (_) => const SagaTimelineScreen()));
                },
              ),

              const SizedBox(height: 12),

              // 5. CU10: Cobros y Pagos QR Idempotentes
              _buildFeatureCard(
                titulo: 'CU10: Cobros y Pagos QR Idempotentes',
                subtitulo: 'Generación dinámica EMVCo y blindaje contra doble cobro en DynamoDB.',
                icono: Icons.qr_code_2_rounded,
                colorIcono: AegisTheme.success,
                onTap: () {
                  Navigator.push(context, MaterialPageRoute(builder: (_) => const QrPaymentScreen()));
                },
              ),

              const SizedBox(height: 12),

              // 6. CU15: Asistente de Reportes por Voz MCP
              _buildFeatureCard(
                titulo: 'CU15: Asistente Pericial de Reportes por Voz (MCP)',
                subtitulo: 'Consultas en lenguaje natural, blindaje Anti-SQLi y reportes en Excel, PDF y Word.',
                icono: Icons.mic_rounded,
                colorIcono: AegisTheme.primary,
                badge: 'Whisper STT',
                onTap: _mostrarAsistenteVozMcp,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMetricCard({
    required String titulo,
    required String valor,
    required IconData icono,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
      decoration: AegisTheme.glassCardDecoration(borderColor: color.withOpacity(0.3)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icono, color: color, size: 22),
          const SizedBox(height: 8),
          Text(
            valor,
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.w800,
              color: color,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            titulo,
            style: const TextStyle(fontSize: 10, color: AegisTheme.textMuted, fontWeight: FontWeight.w600),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  Widget _buildFeatureCard({
    required String titulo,
    required String subtitulo,
    required IconData icono,
    required Color colorIcono,
    String? badge,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: AegisTheme.glassCardDecoration(),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: colorIcono.withOpacity(0.15),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icono, color: colorIcono, size: 26),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Flexible(
                        child: Text(
                          titulo,
                          style: const TextStyle(
                            color: AegisTheme.textPrimary,
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      if (badge != null)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: AegisTheme.warning.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: AegisTheme.warning, width: 0.8),
                          ),
                          child: Text(
                            badge,
                            style: const TextStyle(color: AegisTheme.warning, fontSize: 10, fontWeight: FontWeight.bold),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitulo,
                    style: const TextStyle(color: AegisTheme.textSecondary, fontSize: 12),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            const Icon(Icons.arrow_forward_ios, size: 14, color: AegisTheme.textMuted),
          ],
        ),
      ),
    );
  }
}
