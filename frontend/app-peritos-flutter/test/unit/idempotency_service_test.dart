import 'package:flutter_test/flutter_test.dart';
import 'package:aegiscore_peritos/core/idempotency/idempotency_service.dart';

void main() {
  group('Core: IdempotencyService (Contrato CU08 & CU10)', () {
    test('debe generar una clave de idempotencia en formato UUIDv4 estricto', () {
      final key1 = IdempotencyService.generateIdempotencyKey();
      final key2 = IdempotencyService.generateIdempotencyKey();

      final uuidv4Regex = RegExp(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
        caseSensitive: false,
      );

      expect(uuidv4Regex.hasMatch(key1), isTrue);
      expect(uuidv4Regex.hasMatch(key2), isTrue);
      expect(key1, isNot(equals(key2)));
    });

    test('debe calcular hash SHA-256 determinista de 64 caracteres hexadecimales', () {
      final payload = {
        'reclamoId': 'REC-2026-00050',
        'montoEstimadoTotal': 3000.0,
      };

      final hash1 = IdempotencyService.calculatePayloadHash(payload);
      final hash2 = IdempotencyService.calculatePayloadHash(payload);

      expect(hash1, equals(hash2));
      expect(hash1.length, equals(64));
      expect(RegExp(r'^[a-f0-9]{64}$').hasMatch(hash1), isTrue);
    });

    test('debe construir encabezados con Idempotency-Key y X-Client-Id', () {
      const customKey = 'a1b2c3d4-e5f6-4a1b-9c2d-112233445566';
      final headers = IdempotencyService.buildHeaders(
        idempotencyKey: customKey,
        clientId: 'FLUTTER_MOBILE',
      );

      expect(headers['Idempotency-Key'], equals(customKey));
      expect(headers['X-Client-Id'], equals('FLUTTER_MOBILE'));
      expect(headers['Content-Type'], equals('application/json'));
    });
  });
}
