import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../core/theme/aegis_theme.dart';
import '../../core/database/database_helper.dart';
import '../../core/config/app_config.dart';
import '../../core/network/api_client.dart';

class SyncQueueScreen extends StatefulWidget {
  const SyncQueueScreen({super.key});

  @override
  State<SyncQueueScreen> createState() => _SyncQueueScreenState();
}

class _SyncQueueScreenState extends State<SyncQueueScreen> {
  List<Map<String, dynamic>> _inspeccionesPendientes = [];
  bool _isLoading = true;
  bool _isSyncing = false;
  String? _syncReportMessage;

  final currencyFormatter = NumberFormat.currency(locale: 'es_BO', symbol: 'BOB ');

  @override
  void initState() {
    super.initState();
    _cargarCola();
  }

  Future<void> _cargarCola() async {
    setState(() => _isLoading = true);
    final pendientes = await DatabaseHelper.instance.obtenerInspeccionesPendientes();
    setState(() {
      _inspeccionesPendientes = pendientes;
      _isLoading = false;
    });
  }

  Future<void> _ejecutarSincronizacionIdempotente() async {
    if (_inspeccionesPendientes.isEmpty) return;

    setState(() {
      _isSyncing = true;
      _syncReportMessage = null;
    });

    int sincronizadosOk = 0;
    int cacheHits = 0;
    int fallidos = 0;

    for (final inspeccion in _inspeccionesPendientes) {
      final id = inspeccion['id'] as int;
      final reclamoId = inspeccion['reclamo_id'] as String;
      final peritoId = inspeccion['perito_id'] as String;
      final montoTotal = inspeccion['monto_estimado_total'] as double;
      final observaciones = inspeccion['observaciones'] as String? ?? '';
      final idempotencyKey = inspeccion['idempotency_key'] as String;

      // Obtener partes asociadas
      final partesDb = await DatabaseHelper.instance.obtenerPartesDeInspeccion(id);
      final partesFormatted = partesDb.map((p) => {
        'parte': p['parte'],
        'severidad': p['severidad'],
        'costoEstimado': p['costo_estimado'],
        'confianzaIa': p['confianza_ia'] ?? 0.9,
      }).toList();

      final payload = {
        'reclamoId': reclamoId,
        'peritoId': peritoId,
        'partesDanadas': partesFormatted,
        'montoEstimadoTotal': montoTotal,
        'fotosEvidencia': ['http://aegiscore.local/evidencias/peritaje_foto1.jpg'],
        'observaciones': observaciones,
        'sincronizadoOffline': true,
        'hashIntegridadOffline': inspeccion['payload_hash'],
      };

      // Envío idempotente con el mismo Idempotency-Key
      final response = await ApiClient.instance.postWithIdempotency(
        url: AppConfig.endpointSyncPeritaje,
        body: payload,
        customIdempotencyKey: idempotencyKey,
      );

      if (response.isSuccess) {
        await DatabaseHelper.instance.marcarInspeccionSincronizada(id, idempotencyKey);
        sincronizadosOk++;
        if (response.isCacheHit) {
          cacheHits++;
        }
      } else {
        fallidos++;
      }
    }

    await _cargarCola();

    setState(() {
      _isSyncing = false;
      _syncReportMessage = 'Sincronización finalizada:\n'
          '• Exitosos en MongoDB: $sincronizadosOk\n'
          '• Replay Cache HIT en DynamoDB (<5ms): $cacheHits\n'
          '• Fallos de conexión: $fallidos';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Cola de Sincronización Idempotente (CU08)'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _cargarCola,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AegisTheme.primary))
          : Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Banner de Estado de Conexión
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: AegisTheme.glassCardDecoration(
                      borderColor: _inspeccionesPendientes.isEmpty ? AegisTheme.success : AegisTheme.warning,
                    ),
                    child: Row(
                      children: [
                        Icon(
                          _inspeccionesPendientes.isEmpty ? Icons.cloud_done : Icons.cloud_upload_outlined,
                          color: _inspeccionesPendientes.isEmpty ? AegisTheme.success : AegisTheme.warning,
                          size: 32,
                        ),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                _inspeccionesPendientes.isEmpty
                                    ? 'TODO AL DÍA CON DYNAMODB Y MONGO'
                                    : '${_inspeccionesPendientes.length} REGISTROS PENDIENTES',
                                style: TextStyle(
                                  color: _inspeccionesPendientes.isEmpty ? AegisTheme.success : AegisTheme.warning,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 14,
                                  letterSpacing: 0.5,
                                ),
                              ),
                              const SizedBox(height: 2),
                              const Text(
                                'Protocolo UUIDv4 + Hash SHA-256 previene duplicidad ante pérdida de señal.',
                                style: TextStyle(color: AegisTheme.textSecondary, fontSize: 12),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 16),

                  if (_syncReportMessage != null) ...[
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AegisTheme.surfaceElevated,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: AegisTheme.primary),
                      ),
                      child: Text(
                        _syncReportMessage!,
                        style: const TextStyle(color: AegisTheme.primary, fontSize: 13, fontWeight: FontWeight.w600),
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],

                  // Lista de Registros en SQLite
                  Expanded(
                    child: _inspeccionesPendientes.isEmpty
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.inventory_2_outlined, size: 64, color: AegisTheme.textMuted.withOpacity(0.5)),
                                const SizedBox(height: 12),
                                const Text(
                                  'No hay peritajes pendientes por sincronizar.',
                                  style: TextStyle(color: AegisTheme.textSecondary),
                                ),
                              ],
                            ),
                          )
                        : ListView.separated(
                            itemCount: _inspeccionesPendientes.length,
                            separatorBuilder: (_, _) => const SizedBox(height: 12),
                            itemBuilder: (context, index) {
                              final item = _inspeccionesPendientes[index];
                              return Card(
                                child: Padding(
                                  padding: const EdgeInsets.all(14),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Row(
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          Text(
                                            item['reclamo_id'],
                                            style: const TextStyle(
                                              fontWeight: FontWeight.bold,
                                              fontSize: 15,
                                              color: AegisTheme.textPrimary,
                                            ),
                                          ),
                                          Container(
                                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                            decoration: BoxDecoration(
                                              color: AegisTheme.warning.withOpacity(0.15),
                                              borderRadius: BorderRadius.circular(6),
                                            ),
                                            child: const Text(
                                              'EN COLA SQLITE',
                                              style: TextStyle(color: AegisTheme.warning, fontSize: 11, fontWeight: FontWeight.bold),
                                            ),
                                          ),
                                        ],
                                      ),
                                      const SizedBox(height: 6),
                                      Text(
                                        'Monto Total: ${currencyFormatter.format(item['monto_estimado_total'])}',
                                        style: const TextStyle(color: AegisTheme.primary, fontWeight: FontWeight.w700),
                                      ),
                                      const SizedBox(height: 8),
                                      // Idempotency-Key (UUIDv4)
                                      Row(
                                        children: [
                                          const Icon(Icons.key, size: 14, color: AegisTheme.textMuted),
                                          const SizedBox(width: 6),
                                          Expanded(
                                            child: Text(
                                              'Idempotency-Key: ${item['idempotency_key'] ?? 'AUTO_UUID'}',
                                              style: const TextStyle(color: AegisTheme.textMuted, fontSize: 11, fontFamily: 'monospace'),
                                              overflow: TextOverflow.ellipsis,
                                            ),
                                          ),
                                        ],
                                      ),
                                      // Payload Hash SHA-256
                                      Row(
                                        children: [
                                          const Icon(Icons.tag, size: 14, color: AegisTheme.textMuted),
                                          const SizedBox(width: 6),
                                          Expanded(
                                            child: Text(
                                              'SHA-256: ${item['payload_hash'] ?? 'CALCULANDO'}',
                                              style: const TextStyle(color: AegisTheme.textMuted, fontSize: 11, fontFamily: 'monospace'),
                                              overflow: TextOverflow.ellipsis,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                              );
                            },
                          ),
                  ),

                  const SizedBox(height: 16),

                  // Botón Sincronizar
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: AegisTheme.primary,
                      foregroundColor: Colors.black,
                    ),
                    onPressed: (_isSyncing || _inspeccionesPendientes.isEmpty)
                        ? null
                        : _ejecutarSincronizacionIdempotente,
                    icon: _isSyncing
                        ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.black, strokeWidth: 2))
                        : const Icon(Icons.sync_rounded),
                    label: Text(
                      _isSyncing
                          ? 'SINCRONIZANDO CON NUBE...'
                          : 'SINCRONIZAR COLA CON MS2 Y DYNAMODB',
                      style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
