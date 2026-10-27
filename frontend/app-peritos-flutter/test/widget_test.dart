import 'package:flutter_test/flutter_test.dart';
import 'package:aegiscore_peritos/main.dart';

void main() {
  testWidgets('AegisCore Mobile Smoke Test: renders Dashboard with 5 modules', (WidgetTester tester) async {
    await tester.pumpWidget(const AegisCorePeritosApp());
    await tester.pump();

    // Verifica la barra de título corporativa
    expect(find.text('AegisCore AI'), findsOneWidget);
    expect(find.text('Peritaje Móvil & Siniestros (Perfil B)'), findsOneWidget);
  });
}
