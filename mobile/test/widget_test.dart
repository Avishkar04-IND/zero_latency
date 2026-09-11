import 'package:flutter_test/flutter_test.dart';
import 'package:smart_medicine_mobile/shared/experience_selector.dart';

void main() {
  testWidgets('ExperienceSelectorApp renders accessibility home title test', (WidgetTester tester) async {
    await tester.pumpWidget(const ExperienceSelectorApp());
    expect(find.textContaining('ZERO LATENCY'), findsWidgets);
  });
}
