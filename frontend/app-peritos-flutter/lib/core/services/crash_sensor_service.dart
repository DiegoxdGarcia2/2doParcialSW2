import 'dart:async';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:sensors_plus/sensors_plus.dart';
import 'push_notification_service.dart';

/// Servicio de Telemetría y Sensor de Impacto Vehicular (CU06 / Criterio ② Examen)
/// Monitorea el acelerómetro nativo del dispositivo y dispara alertas automáticas ante desaceleración violenta.
class CrashSensorService {
  static final CrashSensorService _instance = CrashSensorService._internal();
  factory CrashSensorService() => _instance;
  CrashSensorService._internal();

  StreamSubscription<UserAccelerometerEvent>? _accelerometerSub;
  bool _isMonitoring = false;
  
  // Umbral de impacto violento: aceleración neta > 24 m/s² (~ 2.5 G)
  static const double impactThreshold = 24.0;
  
  DateTime? _lastAlertTime;

  bool get isMonitoring => _isMonitoring;

  void startMonitoring({Function(double gForce)? onImpactDetected}) {
    if (_isMonitoring) return;

    try {
      _accelerometerSub = userAccelerometerEventStream().listen(
        (UserAccelerometerEvent event) {
          // Magnitud euclidiana del vector aceleración: sqrt(x² + y² + z²)
          final double magnitude = sqrt(event.x * event.x + event.y * event.y + event.z * event.z);

          if (magnitude > impactThreshold) {
            final now = DateTime.now();
            // Evitar spam de alertas repetitivas (cooldown de 10 segundos)
            if (_lastAlertTime == null || now.difference(_lastAlertTime!).inSeconds > 10) {
              _lastAlertTime = now;
              final double gForce = magnitude / 9.80665;
              debugPrint('[CrashSensor] 💥 IMPACTO DETECTADO: ${magnitude.toStringAsFixed(1)} m/s² (${gForce.toStringAsFixed(1)} G)');

              PushNotificationService().showEmergencyAlert(
                title: 'Impacto Vehicular Detectado (${gForce.toStringAsFixed(1)} G)',
                body: 'El sensor de aceleración registró desaceleración violenta. Protocolo de emergencia SOS activado.',
                metadata: {
                  'magnitude': magnitude,
                  'gForce': gForce,
                  'timestamp': now.toIso8601String(),
                },
              );

              if (onImpactDetected != null) {
                onImpactDetected(gForce);
              }
            }
          }
        },
        onError: (err) {
          debugPrint('[CrashSensor] Sensor no disponible o error de hardware: $err');
        },
      );

      _isMonitoring = true;
      debugPrint('[CrashSensor] Monitoreo de acelerómetro activado.');
    } catch (e) {
      debugPrint('[CrashSensor] Excepción inicializando sensor: $e');
    }
  }

  void stopMonitoring() {
    _accelerometerSub?.cancel();
    _accelerometerSub = null;
    _isMonitoring = false;
    debugPrint('[CrashSensor] Monitoreo de acelerómetro detenido.');
  }
}
