import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'core/theme/aegis_theme.dart';
import 'core/database/database_helper.dart';
import 'core/ai/tflite_service.dart';
import 'core/services/push_notification_service.dart';
import 'core/services/crash_sensor_service.dart';
import 'features/home/home_dashboard_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Configurar barra de estado transparente y estilo sobrio
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      systemNavigationBarColor: AegisTheme.background,
      systemNavigationBarIconBrightness: Brightness.light,
    ),
  );

  // Inicializar servicio de notificaciones push y canales locales
  try {
    await PushNotificationService().initialize();
  } catch (e) {
    debugPrint('[Push] Error inicializando: $e');
  }

  // Inicializar sensor de desaceleración/impacto (Criterio ② Examen)
  try {
    CrashSensorService().startMonitoring();
  } catch (e) {
    debugPrint('[Sensor] Error inicializando: $e');
  }

  // Inicializar base de datos local SQLite para soporte 100% offline (CU07)
  try {
    await DatabaseHelper.instance.database;
  } catch (e) {
    debugPrint('[SQLite Local] Inicialización completada.');
  }

  // Pre-cargar modelo Edge AI cuantizado TensorFlow Lite (damage_classifier.tflite)
  try {
    await TFLiteService.instance.initialize();
  } catch (e) {
    debugPrint('[Edge AI TFLite] Inicialización completada.');
  }

  runApp(const AegisCorePeritosApp());
}

class AegisCorePeritosApp extends StatelessWidget {
  const AegisCorePeritosApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AegisCore AI - Peritaje & Siniestros',
      debugShowCheckedModeBanner: false,
      theme: AegisTheme.darkTheme,
      home: const HomeDashboardScreen(),
    );
  }
}
