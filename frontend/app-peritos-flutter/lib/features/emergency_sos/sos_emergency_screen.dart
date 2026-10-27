import 'package:flutter/material.dart';
import '../../core/theme/aegis_theme.dart';
import '../../core/config/app_config.dart';
import '../../core/network/api_client.dart';
import '../../core/database/database_helper.dart';
import '../../core/idempotency/idempotency_service.dart';

class SosEmergencyScreen extends StatefulWidget {
  const SosEmergencyScreen({super.key});

  @override
  State<SosEmergencyScreen> createState() => _SosEmergencyScreenState();
}

class _SosEmergencyScreenState extends State<SosEmergencyScreen> {
  final _formKey = GlobalKey<FormState>();

  String _polizaId = 'POL-2026-001';
  String _clienteId = 'CLI-8821-PAZ';
  String _descripcion = 'Colisión por alcance en cruce semaforizado';
  String _direccion = 'Av. 6 de Agosto esq. Pinilla, La Paz';
  double _latitud = -16.5050;
  double _longitud = -68.1300;

  int _heridos = 0;
  bool _vehiculoInmovilizado = true;
  bool _airbagDesplegado = false;
  bool _isSubmitting = false;

  String get _severidadCalculada {
    if (_heridos > 0 || _airbagDesplegado) return 'GRAVE';
    if (_vehiculoInmovilizado) return 'MODERADO';
    return 'LEVE';
  }

  Color get _colorSeveridad {
    switch (_severidadCalculada) {
      case 'GRAVE':
        return AegisTheme.emergency;
      case 'MODERADO':
        return AegisTheme.warning;
      default:
        return AegisTheme.success;
    }
  }

  Future<void> _enviarReporteSos() async {
    if (!_formKey.currentState!.validate()) return;
    _formKey.currentState!.save();

    setState(() => _isSubmitting = true);

    final idempotencyKey = IdempotencyService.generateIdempotencyKey();
    final payload = {
      'polizaId': _polizaId,
      'clienteId': _clienteId,
      'latitud': _latitud,
      'longitud': _longitud,
      'descripcion': _descripcion,
      'direccion': _direccion,
      'heridos': _heridos,
      'vehiculoInmovilizado': _vehiculoInmovilizado,
      'airbagDesplegado': _airbagDesplegado,
      'fotosPreliminares': [
        'http://aegiscore.local/evidencias/sos_frontal.jpg'
      ],
    };

    final response = await ApiClient.instance.postWithIdempotency(
      url: AppConfig.endpointSosEmergency,
      body: payload,
      customIdempotencyKey: idempotencyKey,
    );

    setState(() => _isSubmitting = false);

    if (response.isSuccess) {
      _mostrarDialogoExito(
        titulo: '🚨 Siniestro SOS Reportado',
        mensaje: 'Expediente: ${response.data['reclamoId'] ?? 'REC-2026-ACTIVO'}\n'
            'Severidad asignada: $_severidadCalculada\n'
            'Triaje automático notificado a peritos cercanos vía FCM Push.',
      );
    } else {
      // Guardar en SQLite Local Offline
      await DatabaseHelper.instance.insertarSosLocal({
        'poliza_id': _polizaId,
        'cliente_id': _clienteId,
        'latitud': _latitud,
        'longitud': _longitud,
        'direccion': _direccion,
        'descripcion': _descripcion,
        'severidad': _severidadCalculada,
        'heridos': _heridos,
        'vehiculo_inmovilizado': _vehiculoInmovilizado ? 1 : 0,
        'airbag_desplegado': _airbagDesplegado ? 1 : 0,
        'estado_sync': 'PENDIENTE',
        'idempotency_key': idempotencyKey,
        'created_at': DateTime.now().toIso8601String(),
      });

      _mostrarDialogoExito(
        titulo: '📡 Guardado en Cola Offline (CU06)',
        mensaje: 'Sin cobertura con la nube. El siniestro SOS fue almacenado '
            'en SQLite local con clave de idempotencia protegida.\n\n'
            'Se sincronizará automáticamente en cuanto recuperes señal.',
      );
    }
  }

  void _mostrarDialogoExito({required String titulo, required String mensaje}) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AegisTheme.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: AegisTheme.surfaceBorder),
        ),
        title: Text(titulo, style: const TextStyle(color: AegisTheme.textPrimary)),
        content: Text(mensaje, style: const TextStyle(color: AegisTheme.textSecondary)),
        actions: [
          ElevatedButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              Navigator.of(context).pop();
            },
            child: const Text('Entendido'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Reporte de Emergencia SOS (CU06)'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Banner Alerta SOS
              Container(
                padding: const EdgeInsets.all(16),
                decoration: AegisTheme.glassCardDecoration(
                  borderColor: AegisTheme.emergency.withOpacity(0.5),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: AegisTheme.emergency.withOpacity(0.15),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.emergency_rounded, color: AegisTheme.emergency, size: 30),
                    ),
                    const SizedBox(width: 14),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'ASISTENCIA INMEDIATA',
                            style: TextStyle(
                              color: AegisTheme.emergency,
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                              letterSpacing: 1,
                            ),
                          ),
                          SizedBox(height: 2),
                          Text(
                            'Reporte directo a central de peritaje y asistencia médica.',
                            style: TextStyle(color: AegisTheme.textSecondary, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Triaje Automático Badge
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  color: _colorSeveridad.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: _colorSeveridad, width: 1.2),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Triaje Automático Preliminar:',
                      style: TextStyle(color: AegisTheme.textPrimary, fontWeight: FontWeight.w600),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                      decoration: BoxDecoration(
                        color: _colorSeveridad,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        _severidadCalculada,
                        style: const TextStyle(
                          color: Colors.black,
                          fontWeight: FontWeight.w800,
                          fontSize: 12,
                          letterSpacing: 0.5,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // Parámetros de Triaje
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Evaluación de Severidad In-Situ',
                        style: TextStyle(color: AegisTheme.textPrimary, fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                      const SizedBox(height: 14),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Personas lesionadas o heridas:'),
                          Row(
                            children: [
                              IconButton(
                                icon: const Icon(Icons.remove_circle_outline, color: AegisTheme.primary),
                                onPressed: _heridos > 0 ? () => setState(() => _heridos--) : null,
                              ),
                              Text('$_heridos', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                              IconButton(
                                icon: const Icon(Icons.add_circle_outline, color: AegisTheme.primary),
                                onPressed: () => setState(() => _heridos++),
                              ),
                            ],
                          ),
                        ],
                      ),
                      const Divider(color: AegisTheme.surfaceBorder),
                      SwitchListTile(
                        contentPadding: EdgeInsets.zero,
                        title: const Text('Vehículo inmovilizado o pérdida de fluidos:'),
                        value: _vehiculoInmovilizado,
                        activeThumbColor: AegisTheme.warning,
                        onChanged: (val) => setState(() => _vehiculoInmovilizado = val),
                      ),
                      const Divider(color: AegisTheme.surfaceBorder),
                      SwitchListTile(
                        contentPadding: EdgeInsets.zero,
                        title: const Text('Bolsas de aire (Airbags) desplegadas:'),
                        value: _airbagDesplegado,
                        activeThumbColor: AegisTheme.emergency,
                        onChanged: (val) => setState(() => _airbagDesplegado = val),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 20),

              // Datos del Asegurado y Ubicación GPS
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Geolocalización GPS y Póliza',
                        style: TextStyle(color: AegisTheme.textPrimary, fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                      const SizedBox(height: 14),
                      TextFormField(
                        initialValue: _polizaId,
                        decoration: const InputDecoration(labelText: 'Código de Póliza'),
                        onSaved: (val) => _polizaId = val ?? '',
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        initialValue: _direccion,
                        decoration: const InputDecoration(
                          labelText: 'Ubicación GPS Detectada',
                          prefixIcon: Icon(Icons.location_on, color: AegisTheme.primary),
                        ),
                        onSaved: (val) => _direccion = val ?? '',
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        initialValue: _descripcion,
                        maxLines: 2,
                        decoration: const InputDecoration(labelText: 'Breve descripción de los hechos'),
                        onSaved: (val) => _descripcion = val ?? '',
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 28),

              // Botón de Envío SOS
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AegisTheme.emergency,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                onPressed: _isSubmitting ? null : _enviarReporteSos,
                icon: _isSubmitting
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Icon(Icons.send_rounded, color: Colors.white),
                label: Text(
                  _isSubmitting ? 'TRANSMITIENDO SOS...' : 'ENVIAR ALERTA SOS INMEDIATA',
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 15),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
