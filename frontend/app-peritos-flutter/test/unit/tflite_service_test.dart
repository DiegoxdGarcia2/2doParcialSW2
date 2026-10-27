import 'package:flutter_test/flutter_test.dart';
import 'package:aegiscore_peritos/core/ai/tflite_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('Core: TFLiteService (Edge AI Clasificación de Daños CU07)', () {
    test('debe clasificar el daño automotriz y devolver una de las 4 etiquetas válidas', () async {
      final service = TFLiteService.instance;
      final result = await service.classifyDamage(hintPart: 'parachoques');

      expect(result.label, equals('parachoques'));
      expect(result.confidence, greaterThanOrEqualTo(0.8));
      expect(result.allProbabilities.containsKey('parachoques'), isTrue);
      expect(result.allProbabilities.containsKey('capó'), isTrue);
      expect(result.allProbabilities.containsKey('puertas'), isTrue);
      expect(result.allProbabilities.containsKey('faroles'), isTrue);
      expect(result.isEdgeAiModelLoaded, isTrue);
    });

    test('debe formatear los nombres de las piezas para presentación formal', () async {
      final service = TFLiteService.instance;
      final result = await service.classifyDamage(hintPart: 'faroles');

      expect(result.labelFormatted, contains('Ópticas / Faroles'));
    });
  });
}
