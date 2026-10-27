import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'package:uuid/uuid.dart';
import '../config/app_config.dart';

class IdempotencyService {
  static const _uuid = Uuid();

  /// Genera una clave de idempotencia estándar UUIDv4
  static String generateIdempotencyKey() {
    return _uuid.v4();
  }

  /// Calcula el hash criptográfico SHA-256 del cuerpo HTTP serializado
  /// según contracts/idempotency-header.spec.json
  static String calculatePayloadHash(Map<String, dynamic> payload) {
    final jsonString = jsonEncode(payload);
    final bytes = utf8.encode(jsonString);
    final digest = sha256.convert(bytes);
    return digest.toString();
  }

  /// Construye los encabezados HTTP obligatorios para llamadas idempotentes
  static Map<String, String> buildHeaders({
    String? idempotencyKey,
    String? clientId,
  }) {
    final key = idempotencyKey ?? generateIdempotencyKey();
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Idempotency-Key': key,
      'X-Client-Id': clientId ?? AppConfig.clientId,
    };
  }
}
