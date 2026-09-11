import 'package:flutter_test/flutter_test.dart';
import 'package:smart_medicine_mobile/main.dart';

void main() {
  testWidgets('App renders placeholder title test', (WidgetTester tester) async {
    await tester.pumpWidget(const SmartMedicineApp());
    expect(find.textContaining('Smart Medicine Platform'), findsOneWidget);
  });
}
