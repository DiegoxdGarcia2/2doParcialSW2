import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import '../../features/notifications/notification_model.dart';

/// Servicio Central de Notificaciones Push y Alertas Locales y Cloud de Alta Prioridad.
/// Conecta la App Móvil con MS4 (LangGraph CU14), MS2 (Siniestros SOS CU06) y MS3 (QR CU10).
class PushNotificationService {
  static final PushNotificationService _instance = PushNotificationService._internal();
  factory PushNotificationService() => _instance;
  PushNotificationService._internal();

  final FlutterLocalNotificationsPlugin _localNotifications = FlutterLocalNotificationsPlugin();

  static const AndroidNotificationChannel _emergencyChannel = AndroidNotificationChannel(
    'aegiscore_emergency_channel',
    'Alertas SOS y Despacho Crítico',
    description: 'Canal prioritario para siniestros viales, detección de impacto y despacho urgente de peritos.',
    importance: Importance.max,
    playSound: true,
    enableVibration: true,
  );

  static const AndroidNotificationChannel _generalChannel = AndroidNotificationChannel(
    'aegiscore_general_channel',
    'Avisos de Peritaje, IA y Cobros QR',
    description: 'Canal para estado de sincronización idempotente, LangGraph CU14, liquidación Saga y confirmación de cobros.',
    importance: Importance.high,
    playSound: true,
  );

  bool _initialized = false;
  static int _idCounter = 100;
  final ValueNotifier<List<NotificationModel>> notificationsNotifier = ValueNotifier<List<NotificationModel>>([]);
  final ValueNotifier<int> unreadCountNotifier = ValueNotifier<int>(0);

  final Set<String> _processedCloudIds = <String>{};
  Timer? _cloudSyncTimer;
  WebSocket? _cloudWebSocket;
  bool _isSyncing = false;

  List<NotificationModel> get notifications => notificationsNotifier.value;
  int get unreadCount => unreadCountNotifier.value;

  /// Inicializa los canales nativos de notificación en Android y la sincronización con el Cloud
  Future<void> initialize() async {
    if (_initialized) return;

    try {
      if (!kIsWeb && Platform.isAndroid) {
        const androidInit = AndroidInitializationSettings('@mipmap/ic_launcher');
        const initSettings = InitializationSettings(android: androidInit);

        await _localNotifications.initialize(
          settings: initSettings,
          onDidReceiveNotificationResponse: _onNotificationTapped,
        );

        final androidPlugin = _localNotifications
            .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();

        if (androidPlugin != null) {
          await androidPlugin.createNotificationChannel(_emergencyChannel);
          await androidPlugin.createNotificationChannel(_generalChannel);
          await androidPlugin.requestNotificationsPermission();
        }
      }

      // Semilla inicial informativa del sistema AegisCore
      if (notificationsNotifier.value.isEmpty) {
        _agregarNotificacionInterna(
          NotificationModel(
            id: 1,
            titulo: 'Sistema AegisCore Conectado',
            mensaje: 'Servicio de notificaciones Push y telemetría de siniestros activo en modo Cloud.',
            tipo: 'info',
            origen: 'sistema',
            leida: false,
            creado: DateTime.now().subtract(const Duration(minutes: 5)).toIso8601String(),
          ),
        );
      }

      _initialized = true;
      debugPrint('[AegisPush] PushNotificationService inicializado exitosamente.');

      // Iniciar sincronización bidireccional continua con LangGraph Cloud (CU14 en MS4)
      iniciarSincronizacionCloud();
    } catch (e) {
      debugPrint('[AegisPush] Error inicializando PushNotificationService: $e');
    }
  }

  /// Inicia el bucle de sincronización con MS4 (Polling cada 4s y WebSocket en tiempo real)
  void iniciarSincronizacionCloud() {
    // 1. Carga inicial de notificaciones persistidas en MongoDB Atlas
    sincronizarNotificacionesCloud(esPrimeraCarga: true);

    // 2. Temporizador periódico de sincronización de fondo cada 4 segundos
    _cloudSyncTimer?.cancel();
    _cloudSyncTimer = Timer.periodic(const Duration(seconds: 4), (_) {
      sincronizarNotificacionesCloud(esPrimeraCarga: false);
    });

    // 3. Conexión WebSocket para recepción instantánea de eventos (< 100ms)
    _conectarWebSocketCloud();
  }

  Future<void> _conectarWebSocketCloud() async {
    if (kIsWeb) return;
    try {
      final wsUrl = AppConfig.endpointAgentWs;
      _cloudWebSocket = await WebSocket.connect(wsUrl).timeout(const Duration(seconds: 6));
      debugPrint('[AegisPush] WebSocket conectado exitosamente a MS4: $wsUrl');

      _cloudWebSocket?.listen(
        (data) {
          debugPrint('[AegisPush] Mensaje en vivo recibido por WebSocket MS4: $data');
          // Dispara sincronización inmediata para alertar al perito en su celular
          sincronizarNotificacionesCloud(esPrimeraCarga: false);
        },
        onError: (e) {
          debugPrint('[AegisPush] Error en canal WebSocket MS4: $e');
          _reintentarConexionWs();
        },
        onDone: () {
          debugPrint('[AegisPush] Canal WebSocket MS4 cerrado.');
          _reintentarConexionWs();
        },
      );
    } catch (e) {
      debugPrint('[AegisPush] Aviso conectando WebSocket MS4 (activo fallback HTTP): $e');
    }
  }

  void _reintentarConexionWs() {
    Timer(const Duration(seconds: 10), () {
      if (_initialized) _conectarWebSocketCloud();
    });
  }

  /// Sincroniza las notificaciones generadas en otros paneles (CU14 LangGraph, MS2 SOS, etc.)
  Future<void> sincronizarNotificacionesCloud({bool esPrimeraCarga = false}) async {
    if (_isSyncing) return;
    _isSyncing = true;

    try {
      final url = Uri.parse('${AppConfig.endpointAgentNotifications}?limit=20');
      final resp = await http.get(url).timeout(const Duration(seconds: 5));

      if (resp.statusCode == 200) {
        final dynamic decoded = jsonDecode(resp.body);
        if (decoded is List) {
          for (final item in decoded) {
            final notifKey = item['id']?.toString() ?? item['_id']?.toString() ?? '';
            if (notifKey.isEmpty) continue;

            final isNew = !_processedCloudIds.contains(notifKey);
            _processedCloudIds.add(notifKey);

            if (isNew) {
              final String titulo = item['titulo']?.toString() ?? 'Alerta de Siniestro (LangGraph)';
              final String mensaje = item['mensaje']?.toString() ?? 'Intervención autónoma registrada en el cluster.';
              final String nivel = item['nivel']?.toString().toUpperCase() ?? 'INFO';
              final String timestamp = item['timestamp']?.toString() ?? DateTime.now().toIso8601String();
              final bool leida = item['leido'] == true;

              final intId = _idCounter++;
              final model = NotificationModel(
                id: intId,
                titulo: titulo,
                mensaje: mensaje,
                tipo: nivel == 'CRITICO' ? 'sos' : 'peritaje',
                origen: 'langgraph_cloud',
                leida: leida,
                creado: timestamp,
                metadata: item is Map<String, dynamic> ? item : null,
              );

              _agregarNotificacionInterna(model);

              // Si NO es la primera carga inicial (es un evento nuevo recién disparado en la nube),
              // hacer sonar y vibrar el teléfono con la notificación nativa de Android:
              if (!esPrimeraCarga && !kIsWeb && (Platform.isAndroid || Platform.isIOS)) {
                await _localNotifications.show(
                  id: intId,
                  title: nivel == 'CRITICO' ? '🚨 $titulo' : '🤖 $titulo',
                  body: mensaje,
                  notificationDetails: NotificationDetails(
                    android: AndroidNotificationDetails(
                      nivel == 'CRITICO' ? _emergencyChannel.id : _generalChannel.id,
                      nivel == 'CRITICO' ? _emergencyChannel.name : _generalChannel.name,
                      channelDescription: _generalChannel.description,
                      icon: '@mipmap/ic_launcher',
                      importance: Importance.max,
                      priority: Priority.high,
                      playSound: true,
                      enableVibration: true,
                      styleInformation: BigTextStyleInformation(mensaje),
                    ),
                  ),
                  payload: jsonEncode(model.toJson()),
                );
              }
            }
          }
        }
      }
    } catch (e) {
      debugPrint('[AegisPush] Aviso en sincronizarNotificacionesCloud: $e');
    } finally {
      _isSyncing = false;
    }
  }

  /// Dispara de forma remota el ciclo autónomo de LangGraph en MS4 (CU14) para pruebas en vivo
  Future<bool> dispararCicloLangGraphDesdeMovil() async {
    try {
      final url = Uri.parse(AppConfig.endpointTriggerCycle);
      final resp = await http.post(url).timeout(const Duration(seconds: 8));
      if (resp.statusCode == 200) {
        await Future.delayed(const Duration(milliseconds: 500));
        await sincronizarNotificacionesCloud(esPrimeraCarga: false);
        return true;
      }
    } catch (e) {
      debugPrint('[AegisPush] Error al disparar ciclo LangGraph: $e');
    }
    return false;
  }

  /// Inyecta un siniestro estancado de prueba en MongoDB Atlas Cloud para forzar remediación y push
  Future<bool> inyectarSiniestroPruebaDesdeMovil() async {
    try {
      final url = Uri.parse(AppConfig.endpointSeedStalledClaim);
      final resp = await http.post(url).timeout(const Duration(seconds: 8));
      if (resp.statusCode == 200) {
        await Future.delayed(const Duration(milliseconds: 500));
        await sincronizarNotificacionesCloud(esPrimeraCarga: false);
        return true;
      }
    } catch (e) {
      debugPrint('[AegisPush] Error al inyectar siniestro prueba: $e');
    }
    return false;
  }

  void _onNotificationTapped(NotificationResponse response) {
    debugPrint('[AegisPush] Notificación seleccionada payload: ${response.payload}');
    if (response.payload != null) {
      try {
        final data = jsonDecode(response.payload!);
        if (data['id'] != null) {
          markAsRead(int.parse(data['id'].toString()));
        }
      } catch (_) {}
    }
  }

  /// Despacha una alerta de emergencia SOS con máxima prioridad, sonido y vibración
  Future<void> showEmergencyAlert({
    required String title,
    required String body,
    Map<String, dynamic>? metadata,
  }) async {
    final int notifId = _idCounter++;
    final model = NotificationModel(
      id: notifId,
      titulo: title,
      mensaje: body,
      tipo: 'sos',
      origen: 'sistema',
      leida: false,
      creado: DateTime.now().toIso8601String(),
      metadata: metadata,
    );

    _agregarNotificacionInterna(model);

    if (!kIsWeb && (Platform.isAndroid || Platform.isIOS)) {
      try {
        await _localNotifications.show(
          id: notifId,
          title: '🚨 $title',
          body: body,
          notificationDetails: NotificationDetails(
            android: AndroidNotificationDetails(
              _emergencyChannel.id,
              _emergencyChannel.name,
              channelDescription: _emergencyChannel.description,
              icon: '@mipmap/ic_launcher',
              importance: Importance.max,
              priority: Priority.high,
              playSound: true,
              enableVibration: true,
              styleInformation: BigTextStyleInformation(body),
            ),
          ),
          payload: jsonEncode(model.toJson()),
        );
      } catch (e) {
        debugPrint('[AegisPush] Error mostrando notificación local SOS: $e');
      }
    }
  }

  /// Notifica evento de sincronización de peritaje offline o cambio de estado
  Future<void> showPeritajeSyncNotification({
    required String folio,
    required bool exitoso,
    String? detalle,
  }) async {
    final int notifId = _idCounter++;
    final title = exitoso ? 'Sincronización Exitosa: $folio' : 'Error al Sincronizar: $folio';
    final body = detalle ?? (exitoso 
        ? 'El expediente y las evidencias fotográficas fueron persistidos en MongoDB Atlas Cloud.'
        : 'Reintento programado en cola offline SQLite.');

    final model = NotificationModel(
      id: notifId,
      titulo: title,
      mensaje: body,
      tipo: 'peritaje',
      origen: 'perito',
      leida: false,
      creado: DateTime.now().toIso8601String(),
    );

    _agregarNotificacionInterna(model);

    if (!kIsWeb && (Platform.isAndroid || Platform.isIOS)) {
      try {
        await _localNotifications.show(
          id: notifId,
          title: exitoso ? '✅ $title' : '⚠️ $title',
          body: body,
          notificationDetails: NotificationDetails(
            android: AndroidNotificationDetails(
              _generalChannel.id,
              _generalChannel.name,
              channelDescription: _generalChannel.description,
              icon: '@mipmap/ic_launcher',
              importance: Importance.high,
              priority: Priority.high,
            ),
          ),
          payload: jsonEncode(model.toJson()),
        );
      } catch (e) {
        debugPrint('[AegisPush] Error mostrando notificación de peritaje: $e');
      }
    }
  }

  /// Notifica cobro o confirmación de pago QR generado
  Future<void> showQrPaymentNotification({
    required String pagoId,
    required double monto,
    required String moneda,
    required String estado,
  }) async {
    final int notifId = _idCounter++;
    final title = 'Cobro QR Actualizado: $estado';
    final body = 'Pago $pagoId por $monto $moneda procesado en el motor actuarial MS3.';

    final model = NotificationModel(
      id: notifId,
      titulo: title,
      mensaje: body,
      tipo: 'qr',
      origen: 'sistema',
      leida: false,
      creado: DateTime.now().toIso8601String(),
    );

    _agregarNotificacionInterna(model);

    if (!kIsWeb && (Platform.isAndroid || Platform.isIOS)) {
      try {
        await _localNotifications.show(
          id: notifId,
          title: '💳 $title',
          body: body,
          notificationDetails: NotificationDetails(
            android: AndroidNotificationDetails(
              _generalChannel.id,
              _generalChannel.name,
              channelDescription: _generalChannel.description,
              icon: '@mipmap/ic_launcher',
              importance: Importance.high,
              priority: Priority.high,
            ),
          ),
          payload: jsonEncode(model.toJson()),
        );
      } catch (e) {
        debugPrint('[AegisPush] Error mostrando notificación QR: $e');
      }
    }
  }

  void _agregarNotificacionInterna(NotificationModel model) {
    final list = List<NotificationModel>.from(notificationsNotifier.value);
    list.insert(0, model);
    notificationsNotifier.value = list;
    _recalcularNoLeidas();
  }

  void markAsRead(int id) {
    final list = notificationsNotifier.value.map((n) {
      if (n.id == id) {
        return n.copyWith(leida: true);
      }
      return n;
    }).toList();
    notificationsNotifier.value = list;
    _recalcularNoLeidas();
  }

  void markAllAsRead() {
    final list = notificationsNotifier.value.map((n) => n.copyWith(leida: true)).toList();
    notificationsNotifier.value = list;
    _recalcularNoLeidas();
  }

  void clearAll() {
    notificationsNotifier.value = [];
    _recalcularNoLeidas();
  }

  void _recalcularNoLeidas() {
    unreadCountNotifier.value = notificationsNotifier.value.where((n) => !n.leida).length;
  }
}
