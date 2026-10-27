class AppConfig {
  // En teléfono físico conectado por USB con ADB reverse: 127.0.0.1
  // En misma red Wi-Fi LAN: 192.168.1.148
  // En emulador Android Studio: 10.0.2.2
  static String hostIp = '127.0.0.1'; 
  
  static String get ms2BaseUrl => 'http://$hostIp:8002';
  static String get ms3BaseUrl => 'http://$hostIp:8003';

  // Endpoints MS2 Siniestros
  static String get endpointSosEmergency => '$ms2BaseUrl/api/v1/siniestros/sos';
  static String get endpointSyncPeritaje => '$ms2BaseUrl/api/v1/siniestros/peritaje/sync';
  static String get endpointSiniestros => '$ms2BaseUrl/api/v1/siniestros';
  static String get endpointHealthMs2 => '$ms2BaseUrl/health';

  // Endpoints MS3 Actuarial & Cobros
  static String get endpointGenerarQr => '$ms3BaseUrl/api/v1/cobranzas/qr/generar';
  static String get endpointConfirmarQr => '$ms3BaseUrl/api/v1/cobranzas/qr/confirmar';
  static String get endpointSagaStatus => '$ms3BaseUrl/api/actuarial/saga-status';
  static String get endpointHealthMs3 => '$ms3BaseUrl/health';

  // Cliente ID para el protocolo de Idempotencia
  static const String clientId = 'FLUTTER_MOBILE';
}
