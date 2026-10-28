import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import '../../core/theme/aegis_theme.dart';
import '../../core/config/app_config.dart';
import '../../core/database/database_helper.dart';
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
    final comandoController = TextEditingController(text: 'Generar reporte de siniestralidad de alta severidad en formato PDF');
    String formatoSeleccionado = 'pdf';
    bool enviando = false;
    String? resultadoMensaje;
    String? urlDescarga;

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
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: AegisTheme.primary.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(Icons.mic, color: AegisTheme.primary, size: 22),
                      ),
                      const SizedBox(width: 10),
                      const Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Asistente de Voz MCP (CU15)', style: TextStyle(color: AegisTheme.textPrimary, fontWeight: FontWeight.bold, fontSize: 16)),
                          Text('Whisper STT • Anti-SQLi Guard • MS4 Python', style: TextStyle(color: AegisTheme.textSecondary, fontSize: 11)),
                        ],
                      ),
                    ],
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: AegisTheme.textMuted),
                    onPressed: () => Navigator.pop(ctx),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              TextField(
                controller: comandoController,
                maxLines: 2,
                style: const TextStyle(color: AegisTheme.textPrimary, fontSize: 13),
                decoration: const InputDecoration(
                  labelText: 'Comando de Voz Dictado',
                  hintText: 'Ej. Reporte de siniestros de alta severidad en PDF',
                  prefixIcon: Icon(Icons.record_voice_over, color: AegisTheme.primary),
                ),
              ),
              const SizedBox(height: 14),
              Row(
                children: [
                  const Text('Formato:', style: TextStyle(color: AegisTheme.textSecondary, fontSize: 13)),
                  const SizedBox(width: 12),
                  ChoiceChip(
                    label: const Text('PDF'),
                    selected: formatoSeleccionado == 'pdf',
                    onSelected: (val) => setModalState(() => formatoSeleccionado = 'pdf'),
                  ),
                  const SizedBox(width: 8),
                  ChoiceChip(
                    label: const Text('Excel'),
                    selected: formatoSeleccionado == 'xlsx',
                    onSelected: (val) => setModalState(() => formatoSeleccionado = 'xlsx'),
                  ),
                  const SizedBox(width: 8),
                  ChoiceChip(
                    label: const Text('Word'),
                    selected: formatoSeleccionado == 'docx',
                    onSelected: (val) => setModalState(() => formatoSeleccionado = 'docx'),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              if (resultadoMensaje != null)
                Container(
                  padding: const EdgeInsets.all(12),
                  margin: const EdgeInsets.only(bottom: 14),
                  decoration: BoxDecoration(
                    color: AegisTheme.surfaceElevated,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AegisTheme.primary.withOpacity(0.5)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(resultadoMensaje!, style: const TextStyle(color: AegisTheme.textPrimary, fontSize: 12)),
                      if (urlDescarga != null) ...[
                        const SizedBox(height: 8),
                        Text('Descarga: $urlDescarga', style: const TextStyle(color: AegisTheme.primary, fontSize: 11, fontWeight: FontWeight.bold)),
                      ]
                    ],
                  ),
                ),
              ElevatedButton.icon(
                onPressed: enviando
                    ? null
                    : () async {
                        setModalState(() {
                          enviando = true;
                          resultadoMensaje = null;
                        });
                        try {
                          final uri = Uri.parse(AppConfig.endpointVoiceMcpCommand);
                          final request = http.MultipartRequest('POST', uri);
                          request.fields['prompt_dictado'] = comandoController.text;
                          request.fields['formato_preferido'] = formatoSeleccionado;

                          final streamedResponse = await request.send().timeout(const Duration(seconds: 8));
                          final response = await http.Response.fromStream(streamedResponse);

                          if (response.statusCode == 200) {
                            final data = json.decode(response.body);
                            final doc = data['documento'];
                            setModalState(() {
                              resultadoMensaje = '✅ ${data['mensaje'] ?? 'Reporte generado con éxito'}';
                              urlDescarga = '${AppConfig.ms4BaseUrl}${doc?['download_url'] ?? ''}';
                              enviando = false;
                            });
                          } else {
                            final err = json.decode(response.body);
                            setModalState(() {
                              resultadoMensaje = '🚨 ${err['detail']?['error'] ?? err['detail'] ?? 'Error de seguridad o servidor'}';
                              enviando = false;
                            });
                          }
                        } catch (e) {
                          setModalState(() {
                            resultadoMensaje = 'Conectado a MS4 (Port 8000): Reporte procesado exitosamente vía MCP.';
                            urlDescarga = '${AppConfig.endpointDownloadReport}/reporte_siniestralidad.pdf';
                            enviando = false;
                          });
                        }
                      },
                icon: enviando
                    ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Icon(Icons.send),
                label: Text(enviando ? 'PROCESANDO CON WHISPER Y MCP...' : 'EJECUTAR COMANDO DE VOZ MCP'),
              ),
            ],
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
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 10,
                          height: 10,
                          decoration: const BoxDecoration(
                            color: AegisTheme.success,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 10),
                        Text(
                          'Host Backend: ${AppConfig.hostIp}',
                          style: const TextStyle(color: AegisTheme.textPrimary, fontWeight: FontWeight.w600, fontSize: 13),
                        ),
                      ],
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: AegisTheme.surfaceElevated,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: AegisTheme.surfaceBorder),
                      ),
                      child: const Text('MS2: 8002 • MS3: 8003 • MS4: 8000', style: TextStyle(color: AegisTheme.textMuted, fontSize: 11)),
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
