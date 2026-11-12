import 'package:flutter_test/flutter_test.dart';
import 'package:aegiscore_peritos/core/services/push_notification_service.dart';
import 'package:aegiscore_peritos/features/notifications/notification_model.dart';
import 'package:aegiscore_peritos/core/config/app_config.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('PushNotificationService & NotificationModel Tests (Perfil B)', () {
    late PushNotificationService pushService;

    setUp(() {
      pushService = PushNotificationService();
      pushService.clearAll();
    });

    test('1. NotificationModel serialización JSON y formateo horario', () {
      final now = DateTime.now().toIso8601String();
      final model = NotificationModel(
        id: 101,
        titulo: 'Siniestro de Emergencia SOS',
        mensaje: 'Colisión frontal en 4to anillo. Despacho pericial solicitado.',
        tipo: 'sos',
        origen: 'sistema',
        leida: false,
        creado: now,
        metadata: {'severidad': 'GRAVE', 'lat': -17.78, 'lng': -63.18},
      );

      final json = model.toJson();
      expect(json['id'], 101);
      expect(json['tipo'], 'sos');
      expect(json['metadata']['severidad'], 'GRAVE');

      final deserialized = NotificationModel.fromJson(json);
      expect(deserialized.id, 101);
      expect(deserialized.titulo, model.titulo);
      expect(deserialized.timeFormatted.isNotEmpty, true);
    });

    test('2. PushNotificationService agrega notificaciones y actualiza conteo no leídas', () async {
      expect(pushService.unreadCount, 0);

      await pushService.showEmergencyAlert(
        title: 'Alerta Choque Violento',
        body: 'Acelerómetro reporta impacto 3.1 G en Av. Banzer.',
      );

      expect(pushService.notifications.length, 1);
      expect(pushService.unreadCount, 1);
      expect(pushService.notifications.first.tipo, 'sos');

      await pushService.showPeritajeSyncNotification(
        folio: 'FOL-2026-991',
        exitoso: true,
      );

      expect(pushService.notifications.length, 2);
      expect(pushService.unreadCount, 2);

      // Marcar una como leída
      final firstId = pushService.notifications.first.id;
      pushService.markAsRead(firstId);
      expect(pushService.unreadCount, 1);

      // Marcar todas leídas
      pushService.markAllAsRead();
      expect(pushService.unreadCount, 0);
    });

    test('3. AppConfig resuelve endpoints de Producción Multi-Cloud por defecto', () {
      AppConfig.isProduction = true;

      expect(AppConfig.ms1BaseUrl, contains('run.app'));
      expect(AppConfig.ms2BaseUrl, 'https://6czu0fuvw6.execute-api.us-east-2.amazonaws.com');
      expect(AppConfig.ms3BaseUrl, contains('azurecontainerapps.io'));
      expect(AppConfig.ms4BaseUrl, contains('run.app'));
      expect(AppConfig.endpointSosEmergency, 'https://6czu0fuvw6.execute-api.us-east-2.amazonaws.com/api/v1/siniestros/sos');
      expect(AppConfig.endpointGenerarQr, 'https://aegiscore-ms3-actuarial.mangosea-88948a0a.eastus.azurecontainerapps.io/api/v1/cobranzas/qr/generar');

      // Alternar a Local
      AppConfig.isProduction = false;
      AppConfig.hostIp = '192.168.1.50';
      expect(AppConfig.ms2BaseUrl, 'http://192.168.1.50:8002');
      expect(AppConfig.ms3BaseUrl, 'http://192.168.1.50:8003');

      // Restaurar a Producción
      AppConfig.isProduction = true;
      expect(AppConfig.isProduction, true);
    });
  });
}

