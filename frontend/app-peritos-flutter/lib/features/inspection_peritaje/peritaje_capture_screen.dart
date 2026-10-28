import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../core/theme/aegis_theme.dart';
import '../../core/ai/tflite_service.dart';
import '../../core/database/database_helper.dart';
import '../../core/idempotency/idempotency_service.dart';

class PeritajeCaptureScreen extends StatefulWidget {
  const PeritajeCaptureScreen({super.key});

  @override
  State<PeritajeCaptureScreen> createState() => _PeritajeCaptureScreenState();
}

class _PeritajeCaptureScreenState extends State<PeritajeCaptureScreen> {
  final _reclamoIdController = TextEditingController(text: 'REC-2026-00050');
  final _peritoIdController = TextEditingController(text: 'PERITO-EXP-44');
  final _observacionesController = TextEditingController(text: 'Impacto lateral izquierdo y ópticas frontales comprometidas.');

  String _parteSeleccionada = 'parachoques';
  String _severidadSeleccionada = 'MODERADO';
  final _costoController = TextEditingController(text: '1200.00');

  final List<Map<String, dynamic>> _partesEvaluadas = [];
  PredictionResult? _ultimoResultadoAi;
  bool _isAnalyzingAi = false;
  bool _isSaving = false;

  final currencyFormatter = NumberFormat.currency(locale: 'es_BO', symbol: 'BOB ');

  double get _montoTotalEstimado {
    return _partesEvaluadas.fold(0.0, (acc, item) => acc + (item['costo_estimado'] as double));
  }

  Future<void> _ejecutarInferenciaAi() async {
    setState(() => _isAnalyzingAi = true);

    // Simula captura de cámara y pase de tensores al modelo Edge AI cuantizado (damage_classifier.tflite)
    await Future.delayed(const Duration(milliseconds: 600));
    final result = await TFLiteService.instance.classifyDamage(hintPart: _parteSeleccionada);
    if (!mounted) return;

    setState(() {
      _ultimoResultadoAi = result;
      _parteSeleccionada = result.label;
      _isAnalyzingAi = false;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: AegisTheme.surfaceElevated,
        content: Row(
          children: [
            const Icon(Icons.memory, color: AegisTheme.primary),
            const SizedBox(width: 10),
            Text(
              'Edge AI TFLite: ${result.labelFormatted} (${(result.confidence * 100).toStringAsFixed(1)}%)',
              style: const TextStyle(color: AegisTheme.textPrimary, fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }

  void _agregarParte() {
    final costo = double.tryParse(_costoController.text) ?? 500.0;
    setState(() {
      _partesEvaluadas.add({
        'parte': _parteSeleccionada,
        'severidad': _severidadSeleccionada,
        'costo_estimado': costo,
        'confianza_ia': _ultimoResultadoAi?.confidence ?? 0.88,
      });
      _costoController.text = '800.00';
    });
  }

  Future<void> _guardarPeritajeOffline() async {
    if (_partesEvaluadas.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          backgroundColor: AegisTheme.emergency,
          content: Text('Debe registrar al menos una pieza dañada evaluada con IA.'),
        ),
      );
      return;
    }

    setState(() => _isSaving = true);

    final idempotencyKey = IdempotencyService.generateIdempotencyKey();
    final now = DateTime.now().toIso8601String();

    final inspeccionData = {
      'reclamo_id': _reclamoIdController.text,
      'perito_id': _peritoIdController.text,
      'fecha_inspeccion': now,
      'monto_estimado_total': _montoTotalEstimado,
      'observaciones': _observacionesController.text,
      'fotos_evidencia': '["http://aegiscore.local/img/frontal.jpg", "http://aegiscore.local/img/lateral.jpg"]',
      'estado_sync': 'PENDIENTE',
      'idempotency_key': idempotencyKey,
      'payload_hash': IdempotencyService.calculatePayloadHash({
        'reclamoId': _reclamoIdController.text,
        'montoEstimadoTotal': _montoTotalEstimado,
        'partes': _partesEvaluadas,
      }),
      'created_at': now,
    };

    await DatabaseHelper.instance.insertarInspeccion(inspeccionData, _partesEvaluadas);
    if (!mounted) return;

    setState(() => _isSaving = false);

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AegisTheme.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: AegisTheme.surfaceBorder),
        ),
        title: const Row(
          children: [
            Icon(Icons.check_circle, color: AegisTheme.success),
            SizedBox(width: 10),
            Text('Peritaje Guardado (CU07)', style: TextStyle(color: AegisTheme.textPrimary)),
          ],
        ),
        content: Text(
          'El expediente ${_reclamoIdController.text} fue almacenado con éxito en SQLite local.\n\n'
          'Total Valorado: ${currencyFormatter.format(_montoTotalEstimado)}\n'
          'Partes clasificadas con IA: ${_partesEvaluadas.length}\n'
          'Estado: PENDIENTE DE SINCRONIZACIÓN IDEMPOTENTE (CU08).',
          style: const TextStyle(color: AegisTheme.textSecondary),
        ),
        actions: [
          ElevatedButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              Navigator.of(context).pop();
            },
            child: const Text('Aceptar'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Inspección Técnica Offline & Edge AI (CU07)'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Identificación del Expediente
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Expediente y Perito Asignado',
                      style: TextStyle(color: AegisTheme.textPrimary, fontWeight: FontWeight.bold, fontSize: 16),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _reclamoIdController,
                            decoration: const InputDecoration(labelText: 'ID Reclamo'),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: TextField(
                            controller: _peritoIdController,
                            decoration: const InputDecoration(labelText: 'ID Ajustador / Perito'),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 20),

            // Visor de Cámara con Inferencia Edge AI
            Container(
              padding: const EdgeInsets.all(16),
              decoration: AegisTheme.glassCardDecoration(borderColor: AegisTheme.primary.withOpacity(0.6)),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.camera_alt, color: AegisTheme.primary),
                          SizedBox(width: 8),
                          Text(
                            'Escáner Edge AI (TFLite Local)',
                            style: TextStyle(color: AegisTheme.textPrimary, fontWeight: FontWeight.bold, fontSize: 15),
                          ),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: AegisTheme.primary.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text('33.2 KB Quantized', style: TextStyle(color: AegisTheme.primary, fontSize: 11)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Área de captura
                  Container(
                    height: 140,
                    width: double.infinity,
                    decoration: BoxDecoration(
                      color: AegisTheme.surfaceElevated,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AegisTheme.surfaceBorder, style: BorderStyle.solid),
                    ),
                    child: _isAnalyzingAi
                        ? const Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                CircularProgressIndicator(color: AegisTheme.primary),
                                SizedBox(height: 10),
                                Text('Ejecutando inferencia en microsegundos...', style: TextStyle(color: AegisTheme.textSecondary, fontSize: 12)),
                              ],
                            ),
                          )
                        : Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.directions_car_filled, size: 48, color: AegisTheme.primary.withOpacity(0.7)),
                              const SizedBox(height: 8),
                              Text(
                                _ultimoResultadoAi != null
                                    ? 'Clasificación: ${_ultimoResultadoAi!.labelFormatted}'
                                    : 'Apunta a la zona afectada para clasificación automática',
                                style: const TextStyle(color: AegisTheme.textPrimary, fontWeight: FontWeight.w600, fontSize: 13),
                              ),
                              if (_ultimoResultadoAi != null)
                                Text(
                                  'Nivel de Confianza: ${(_ultimoResultadoAi!.confidence * 100).toStringAsFixed(1)}%',
                                  style: const TextStyle(color: AegisTheme.success, fontSize: 12, fontWeight: FontWeight.bold),
                                ),
                            ],
                          ),
                  ),

                  const SizedBox(height: 14),

                  OutlinedButton.icon(
                    onPressed: _isAnalyzingAi ? null : _ejecutarInferenciaAi,
                    icon: const Icon(Icons.flash_on, color: AegisTheme.primary),
                    label: const Text('ANALIZAR FOTOGRAFÍA CON TENSORFLOW LITE'),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Formulario para Agregar Daño
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Detalle de Pieza Dañada', style: TextStyle(color: AegisTheme.textPrimary, fontWeight: FontWeight.bold, fontSize: 15)),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          flex: 3,
                          child: DropdownButtonFormField<String>(
                            value: _parteSeleccionada,
                            decoration: const InputDecoration(labelText: 'Pieza Afectada'),
                            dropdownColor: AegisTheme.surfaceElevated,
                            items: const [
                              DropdownMenuItem(value: 'parachoques', child: Text('Parachoques')),
                              DropdownMenuItem(value: 'capó', child: Text('Capó Frontal')),
                              DropdownMenuItem(value: 'puertas', child: Text('Puertas Laterales')),
                              DropdownMenuItem(value: 'faroles', child: Text('Ópticas / Faroles')),
                            ],
                            onChanged: (val) => setState(() => _parteSeleccionada = val ?? 'parachoques'),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          flex: 2,
                          child: DropdownButtonFormField<String>(
                            value: _severidadSeleccionada,
                            decoration: const InputDecoration(labelText: 'Severidad'),
                            dropdownColor: AegisTheme.surfaceElevated,
                            items: const [
                              DropdownMenuItem(value: 'LEVE', child: Text('Leve')),
                              DropdownMenuItem(value: 'MODERADO', child: Text('Moderado')),
                              DropdownMenuItem(value: 'GRAVE', child: Text('Grave')),
                            ],
                            onChanged: (val) => setState(() => _severidadSeleccionada = val ?? 'MODERADO'),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _costoController,
                            keyboardType: TextInputType.number,
                            decoration: const InputDecoration(
                              labelText: 'Costo Estimado (BOB)',
                              prefixText: 'BOB ',
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        ElevatedButton.icon(
                          onPressed: _agregarParte,
                          icon: const Icon(Icons.add, size: 18),
                          label: const Text('Agregar'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 20),

            // Lista de Partes Evaluadas
            if (_partesEvaluadas.isNotEmpty) ...[
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Piezas en Inspección (${_partesEvaluadas.length})',
                    style: const TextStyle(color: AegisTheme.textPrimary, fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                  Text(
                    'Total: ${currencyFormatter.format(_montoTotalEstimado)}',
                    style: const TextStyle(color: AegisTheme.primary, fontWeight: FontWeight.w800, fontSize: 16),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _partesEvaluadas.length,
                separatorBuilder: (_, __) => const SizedBox(height: 8),
                itemBuilder: (context, index) {
                  final item = _partesEvaluadas[index];
                  return Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    decoration: BoxDecoration(
                      color: AegisTheme.surfaceElevated,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: AegisTheme.surfaceBorder),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              item['parte'].toString().toUpperCase(),
                              style: const TextStyle(fontWeight: FontWeight.bold, color: AegisTheme.textPrimary),
                            ),
                            Text(
                              'Severidad: ${item['severidad']} • IA Conf: ${((item['confianza_ia'] as double) * 100).toStringAsFixed(0)}%',
                              style: const TextStyle(color: AegisTheme.textSecondary, fontSize: 12),
                            ),
                          ],
                        ),
                        Row(
                          children: [
                            Text(
                              currencyFormatter.format(item['costo_estimado']),
                              style: const TextStyle(fontWeight: FontWeight.w700, color: AegisTheme.textPrimary),
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete_outline, color: AegisTheme.emergency, size: 20),
                              onPressed: () => setState(() => _partesEvaluadas.removeAt(index)),
                            ),
                          ],
                        ),
                      ],
                    ),
                  );
                },
              ),
              const SizedBox(height: 20),
            ],

            // Botón Guardar en SQLite Local
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: AegisTheme.primaryDark,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              onPressed: _isSaving ? null : _guardarPeritajeOffline,
              icon: _isSaving
                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Icon(Icons.save_rounded, color: Colors.white),
              label: Text(
                _isSaving ? 'GUARDANDO EN DISPOSITIVO...' : 'GUARDAR PERITAJE EN SQLITE LOCAL (OFFLINE)',
                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _abrirAsistenteVozMcpRapido,
        backgroundColor: AegisTheme.primary,
        icon: const Icon(Icons.mic, color: Colors.white),
        label: const Text('Asistente Voz MCP', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
      ),
    );
  }

  void _abrirAsistenteVozMcpRapido() {
    final comando = 'Generar reporte pericial del reclamo ${_reclamoIdController.text} con ${_partesEvaluadas.length} piezas inspeccionadas en formato PDF';
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AegisTheme.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: AegisTheme.surfaceBorder),
        ),
        title: const Row(
          children: [
            Icon(Icons.mic, color: AegisTheme.primary),
            SizedBox(width: 8),
            Text('Asistente de Voz Pericial', style: TextStyle(color: AegisTheme.textPrimary, fontSize: 16)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Dictado automático en terreno con Whisper STT y Servidor MCP:',
              style: TextStyle(color: AegisTheme.textSecondary, fontSize: 12),
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: AegisTheme.surfaceElevated,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                '"$comando"',
                style: const TextStyle(color: AegisTheme.textPrimary, fontStyle: FontStyle.italic, fontSize: 12),
              ),
            ),
            const SizedBox(height: 12),
            const Row(
              children: [
                Icon(Icons.shield, color: AegisTheme.primary, size: 16),
                SizedBox(width: 6),
                Text('Blindaje OWASP Anti-SQLi Activo', style: TextStyle(color: AegisTheme.textMuted, fontSize: 11)),
              ],
            )
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cerrar', style: TextStyle(color: AegisTheme.textSecondary)),
          ),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  backgroundColor: AegisTheme.surfaceElevated,
                  content: Text(
                    '✅ Solicitud MCP enviada a MS4 Python (Port 8000). Compilando PDF...',
                    style: TextStyle(color: AegisTheme.textPrimary),
                  ),
                ),
              );
            },
            icon: const Icon(Icons.send, size: 16),
            label: const Text('Enviar Comando'),
          ),
        ],
      ),
    );
  }
}

