import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:smart_medicine_mobile/shared/models/history_record.dart';
import 'package:smart_medicine_mobile/shared/models/verification_model.dart';
import 'package:smart_medicine_mobile/shared/models/medicine_model.dart';
import 'package:smart_medicine_mobile/shared/models/batch_model.dart';
import 'package:smart_medicine_mobile/services/history/history_service.dart';
import 'package:smart_medicine_mobile/services/history/local_history_service.dart';
import 'package:smart_medicine_mobile/features/accessibility/history/history_controller.dart';
import 'package:smart_medicine_mobile/services/tts/tts_service.dart';

class MockTTSService extends TTSService {
  final List<String> spokenMessages = [];

  @override
  void initTts() {}

  @override
  Future<void> speak(String text, {bool queue = false}) async {
    spokenMessages.add(text);
  }

  @override
  Future<void> stop() async {}
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('HistoryRecord Model Tests', () {
    test('Converts VerificationResult to HistoryRecord accurately', () {
      final nowStr = DateTime.now().toIso8601String();
      final result = VerificationResult(
        isValid: true,
        status: VerificationStatus.authentic,
        medicine: const MedicineModel(
          id: 'med-101',
          name: 'Paracetamol Extra',
          genericName: 'Acetaminophen',
          dosage: '650mg',
          manufacturer: 'Apex Pharma',
          description: 'Pain relief',
          storageInstructions: 'Keep cool',
          warnings: 'Do not exceed dose',
        ),
        batch: const BatchModel(
          id: 'b-101',
          batchNumber: 'PAR-2025-09',
          manufactureDate: '11/09/2026',
          expiryDate: '10/09/2028',
          quantity: 100,
        ),
        scannedAt: nowStr,
        rawCode: 'DATAMATRIX-PAR650',
        message: 'Authentic product',
      );

      final record = HistoryRecord.fromVerificationResult(result);

      expect(record.medicineName, 'Paracetamol Extra 650mg');
      expect(record.verificationStatus, VerificationStatus.authentic);
      expect(record.formattedStatus, 'Verified');
      expect(record.batchNumber, 'PAR-2025-09');
      expect(record.expiryDate, '10/09/2028');
      expect(record.rawCode, 'DATAMATRIX-PAR650');

      final json = record.toJson();
      final rehydrated = HistoryRecord.fromJson(json);

      expect(rehydrated.medicineName, record.medicineName);
      expect(rehydrated.verificationStatus, VerificationStatus.authentic);
      expect(rehydrated.batchNumber, 'PAR-2025-09');
    });

    test('Formats verification status labels correctly without color dependence', () {
      final r1 = HistoryRecord(
        id: '1',
        medicineName: 'Med A',
        verificationStatus: VerificationStatus.authentic,
        timestamp: DateTime.now().toIso8601String(),
        batchNumber: 'B1',
        expiryDate: 'E1',
        rawCode: 'C1',
        message: '',
      );

      final r2 = HistoryRecord(
        id: '2',
        medicineName: 'Med B',
        verificationStatus: VerificationStatus.expired,
        timestamp: DateTime.now().toIso8601String(),
        batchNumber: 'B2',
        expiryDate: 'E2',
        rawCode: 'C2',
        message: '',
      );

      final r3 = HistoryRecord(
        id: '3',
        medicineName: 'Med C',
        verificationStatus: VerificationStatus.suspectedCounterfeit,
        timestamp: DateTime.now().toIso8601String(),
        batchNumber: 'B3',
        expiryDate: 'E3',
        rawCode: 'C3',
        message: '',
      );

      expect(r1.formattedStatus, 'Verified');
      expect(r2.formattedStatus, 'Expired');
      expect(r3.formattedStatus, 'Suspicious');
    });
  });

  group('LocalHistoryService Tests', () {
    late HistoryService historyService;

    setUp(() {
      SharedPreferences.setMockInitialValues({});
      historyService = LocalHistoryService();
    });

    test('Saves record and orders newest first', () async {
      final olderTime = DateTime.now().subtract(const Duration(minutes: 10)).toIso8601String();
      final newerTime = DateTime.now().toIso8601String();

      final rec1 = HistoryRecord(
        id: 'rec-1',
        medicineName: 'Older Scan',
        verificationStatus: VerificationStatus.authentic,
        timestamp: olderTime,
        batchNumber: 'B001',
        expiryDate: '2028-01-01',
        rawCode: 'CODE-001',
        message: 'Authentic',
      );

      final rec2 = HistoryRecord(
        id: 'rec-2',
        medicineName: 'Newer Scan',
        verificationStatus: VerificationStatus.expired,
        timestamp: newerTime,
        batchNumber: 'B002',
        expiryDate: '2023-01-01',
        rawCode: 'CODE-002',
        message: 'Expired',
      );

      await historyService.saveRecord(rec1);
      await historyService.saveRecord(rec2);

      final list = await historyService.getHistoryRecords();
      expect(list.length, 2);
      expect(list.first.id, 'rec-2'); // Newest first
      expect(list.last.id, 'rec-1');
    });

    test('Duplicate scan policy suppresses identical code scanned within 5 seconds', () async {
      final now = DateTime.now();

      final rec1 = HistoryRecord(
        id: 'dup-1',
        medicineName: 'Paracetamol',
        verificationStatus: VerificationStatus.authentic,
        timestamp: now.toIso8601String(),
        batchNumber: 'B100',
        expiryDate: '2028-01-01',
        rawCode: 'SAME-CODE-999',
        message: 'Authentic',
      );

      final rec2 = HistoryRecord(
        id: 'dup-2',
        medicineName: 'Paracetamol',
        verificationStatus: VerificationStatus.authentic,
        timestamp: now.add(const Duration(seconds: 2)).toIso8601String(), // 2s later
        batchNumber: 'B100',
        expiryDate: '2028-01-01',
        rawCode: 'SAME-CODE-999',
        message: 'Authentic',
      );

      await historyService.saveRecord(rec1);
      await historyService.saveRecord(rec2); // Should be suppressed

      final list = await historyService.getHistoryRecords();
      expect(list.length, 1);
      expect(list.first.id, 'dup-1');
    });

    test('Deletes single record correctly', () async {
      final rec1 = HistoryRecord(
        id: 'del-1',
        medicineName: 'Med 1',
        verificationStatus: VerificationStatus.authentic,
        timestamp: DateTime.now().toIso8601String(),
        batchNumber: 'B1',
        expiryDate: 'E1',
        rawCode: 'C1',
        message: '',
      );

      await historyService.saveRecord(rec1);
      var list = await historyService.getHistoryRecords();
      expect(list.length, 1);

      await historyService.deleteRecord('del-1');
      list = await historyService.getHistoryRecords();
      expect(list.isEmpty, true);
    });

    test('Clears all records correctly', () async {
      final rec1 = HistoryRecord(
        id: 'c-1',
        medicineName: 'Med 1',
        verificationStatus: VerificationStatus.authentic,
        timestamp: DateTime.now().subtract(const Duration(seconds: 20)).toIso8601String(),
        batchNumber: 'B1',
        expiryDate: 'E1',
        rawCode: 'CODE-A',
        message: '',
      );

      final rec2 = HistoryRecord(
        id: 'c-2',
        medicineName: 'Med 2',
        verificationStatus: VerificationStatus.authentic,
        timestamp: DateTime.now().toIso8601String(),
        batchNumber: 'B2',
        expiryDate: 'E2',
        rawCode: 'CODE-B',
        message: '',
      );

      await historyService.saveRecord(rec1);
      await historyService.saveRecord(rec2);

      expect((await historyService.getHistoryRecords()).length, 2);

      await historyService.clearHistory();

      expect((await historyService.getHistoryRecords()).isEmpty, true);
    });
  });

  group('HistoryController Tests', () {
    late LocalHistoryService historyService;
    late MockTTSService mockTTS;
    late HistoryController controller;

    setUp(() {
      SharedPreferences.setMockInitialValues({});
      historyService = LocalHistoryService();
      mockTTS = MockTTSService();
      controller = HistoryController(
        historyService: historyService,
        ttsService: mockTTS,
      );
    });

    test('Loads empty history state and speaks accessible message', () async {
      await controller.loadHistory();

      expect(controller.state.isLoading, false);
      expect(controller.state.records.isEmpty, true);
      expect(mockTTS.spokenMessages.contains("You have no scan history yet."), true);
    });

    test('Requests delete confirmation and executes deletion on confirmation', () async {
      final record = HistoryRecord(
        id: 'item-99',
        medicineName: 'Amoxicillin 500mg',
        verificationStatus: VerificationStatus.authentic,
        timestamp: DateTime.now().toIso8601String(),
        batchNumber: 'AMX-01',
        expiryDate: '2027-01-01',
        rawCode: 'AMX-99',
        message: '',
      );

      await historyService.saveRecord(record);
      await controller.loadHistory(speakSummary: false);

      expect(controller.state.records.length, 1);

      controller.requestDeleteConfirmation('item-99');
      expect(controller.state.deleteConfirmationId, 'item-99');
      expect(mockTTS.spokenMessages.last.contains('Delete scan for Amoxicillin 500mg'), true);

      await controller.confirmAndDelete('item-99');
      expect(controller.state.records.isEmpty, true);
      expect(controller.state.deleteConfirmationId, null);
      expect(mockTTS.spokenMessages.contains('Scan record deleted.'), true);
    });

    test('Requests clear all confirmation and executes clear all', () async {
      await historyService.saveRecord(HistoryRecord(
        id: 'item-1',
        medicineName: 'Med 1',
        verificationStatus: VerificationStatus.authentic,
        timestamp: DateTime.now().subtract(const Duration(seconds: 10)).toIso8601String(),
        batchNumber: 'B1',
        expiryDate: 'E1',
        rawCode: 'C1',
        message: '',
      ));

      await controller.loadHistory(speakSummary: false);
      expect(controller.state.records.length, 1);

      controller.requestClearAllConfirmation();
      expect(controller.state.isClearAllConfirming, true);
      expect(mockTTS.spokenMessages.last.contains('clear all scan history'), true);

      await controller.confirmAndClearAll();
      expect(controller.state.records.isEmpty, true);
      expect(controller.state.isClearAllConfirming, false);
      expect(mockTTS.spokenMessages.contains('All scan history cleared.'), true);
    });
  });
}
