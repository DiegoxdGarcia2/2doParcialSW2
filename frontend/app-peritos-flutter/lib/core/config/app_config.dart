/// Configuración central de conectividad y endpoints de AegisCore AI Móvil.
/// Soporta modo Cloud Producción (Multi-Cloud activo) y modo Localhost/LAN para desarrollo.
class AppConfig {
  // Flag global de entorno: Por defecto PRODUCCIÓN CLOUD
  static bool isProduction = true;

  // Host IP para entorno local (USB reverse: 127.0.0.1, Wi-Fi LAN: 192.168.x.x, Emulador: 10.0.2.2)
  static String hostIp = '127.0.0.1';

  // =========================================================================
  // ENDPOINTS OFICIALES DE PRODUCCIÓN MULTI-CLOUD
  // =========================================================================
  // MS1: PHP 8.3 Laravel DDD en Google Cloud Run (us-central1)
  static const String ms1ProductionUrl = 'https://aegiscore-ms1-polizas-400568277774.us-central1.run.app';

  // MS2: NestJS 10 Clean + CQRS en AWS EC2 / ECS Fargate (us-east-2)
  static const String ms2ProductionUrl = 'https://6czu0fuvw6.execute-api.us-east-2.amazonaws.com';

  // MS3: Spring Boot 3 Hexagonal en Azure Container Apps (eastus)
  static const String ms3ProductionUrl = 'https://aegiscore-ms3-actuarial.mangosea-88948a0a.eastus.azurecontainerapps.io';

  // MS4: Python 3.11 IA + MCP Server en Google Cloud Run (us-central1)
  static const String ms4ProductionUrl = 'https://aegiscore-ms4-ia-400568277774.us-central1.run.app';

  // =========================================================================
  // RESOLUTORES DINÁMICOS DE URL BASE
  // =========================================================================
  static String get ms1BaseUrl => isProduction ? ms1ProductionUrl : 'http://$hostIp:8001';
  static String get ms2BaseUrl => isProduction ? ms2ProductionUrl : 'http://$hostIp:8002';
  static String get ms3BaseUrl => isProduction ? ms3ProductionUrl : 'http://$hostIp:8003';
  static String get ms4BaseUrl => isProduction ? ms4ProductionUrl : 'http://$hostIp:8004';

  // =========================================================================
  // ENDPOINTS MS2 SIENIESTROS, TRIAJE Y PERITAJE (AWS)
  // =========================================================================
  static String get endpointSosEmergency => '$ms2BaseUrl/api/v1/siniestros/sos';
  static String get endpointSyncPeritaje => '$ms2BaseUrl/api/v1/siniestros/peritaje/sync';
  static String get endpointSiniestros => '$ms2BaseUrl/api/v1/siniestros';
  static String get endpointGeoCercanos => '$ms2BaseUrl/api/v1/siniestros/geo/cercanos';
  static String get endpointHealthMs2 => '$ms2BaseUrl/health';

  // =========================================================================
  // ENDPOINTS MS3 ACTUARIAL, SAGA Y COBROS QR (AZURE)
  // =========================================================================
  static String get endpointGenerarQr => '$ms3BaseUrl/api/v1/cobranzas/qr/generar';
  static String get endpointConfirmarQr => '$ms3BaseUrl/api/v1/cobranzas/qr/confirmar';
  static String get endpointSagaStatus => '$ms3BaseUrl/api/actuarial/saga-status';
  static String get endpointReservaActuarial => '$ms3BaseUrl/api/v1/actuarial/reserva';
  static String get endpointHealthMs3 => '$ms3BaseUrl/actuator/health';

  // =========================================================================
  // ENDPOINTS MS4 IA, CRASHNET, LANGGRAPH Y SERVIDOR MCP (GCP)
  // =========================================================================
  static String get endpointVoiceMcpCommand => '$ms4BaseUrl/api/v1/mcp/voice-command/json';
  static String get endpointMcpTools => '$ms4BaseUrl/api/v1/mcp/tools';
  static String get endpointDownloadReport => '$ms4BaseUrl/api/v1/mcp/download-report';
  static String get endpointVisionCrashNet => '$ms4BaseUrl/api/v1/ia/vision/inspeccionar-dano';
  static String get endpointHealthMs4 => '$ms4BaseUrl/health';
  static String get endpointAgentNotifications => '$ms4BaseUrl/api/agent/notifications';
  static String get endpointAgentWs => isProduction
      ? 'wss://aegiscore-ms4-ia-400568277774.us-central1.run.app/api/agent/ws'
      : 'ws://$hostIp:8004/api/agent/ws';
  static String get endpointTriggerCycle => '$ms4BaseUrl/api/agent/run-cycle';
  static String get endpointSeedStalledClaim => '$ms4BaseUrl/api/agent/seed-stalled-claim';

  // Identificador del cliente para el protocolo de idempotencia (DynamoDB)
  static const String clientId = 'AEGISCORE_MOBILE_FLUTTER';

  // Etiqueta legible del entorno activo
  static String get environmentLabel => isProduction ? 'Producción Cloud (AWS/Azure/GCP)' : 'Desarrollo Local ($hostIp)';
}
