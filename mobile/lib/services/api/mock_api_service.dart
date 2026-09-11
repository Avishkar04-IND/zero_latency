import 'api_service.dart';
import '../../shared/models/verification_model.dart';
import '../../shared/models/medicine_model.dart';
import '../../shared/models/batch_model.dart';

class MockApiService implements ApiService {
  final List<VerificationResult> _mockHistory = [];

  @override
  Future<VerificationResult> verifyCode(String codeData, {double? lat, double? lng}) async {
    await Future.delayed(const Duration(milliseconds: 600));

    VerificationResult result;

    if (codeData.contains('EXPIRED') || codeData.contains('EXP')) {
      result = VerificationResult(
        isValid: false,
        status: VerificationStatus.expired,
        medicine: const MedicineModel(
          id: 'med-002',
          name: 'Amoxicillin Trihydrate',
          dosage: '500mg',
          manufacturer: 'Astra Biotech Labs',
          description: 'Antibiotic for bacterial infections.',
          storageInstructions: 'Store below 25 degrees Celsius.',
          warnings: 'Complete full course. Do not take if allergic to penicillin.',
        ),
        batch: const BatchModel(
          id: 'batch-987',
          batchNumber: 'AMX-2023-88',
          manufactureDate: '2023-01-10',
          expiryDate: '2024-01-10',
          quantity: 500,
        ),
        scannedAt: DateTime.now().toIso8601String(),
        rawCode: codeData,
        message: 'Medicine batch is expired.',
      );
    } else if (codeData.contains('FAKE') || codeData.contains('INVALID')) {
      result = VerificationResult(
        isValid: false,
        status: VerificationStatus.suspectedCounterfeit,
        scannedAt: DateTime.now().toIso8601String(),
        rawCode: codeData,
        message: 'Suspected counterfeit code detected.',
      );
    } else {
      result = VerificationResult(
        isValid: true,
        status: VerificationStatus.authentic,
        medicine: const MedicineModel(
          id: 'med-001',
          name: 'Paracetamol Extra',
          dosage: '650mg',
          manufacturer: 'Apex Pharma Global',
          description: 'Analgesic and antipyretic for pain and fever relief.',
          storageInstructions: 'Keep in a cool dry place away from direct sunlight.',
          warnings: 'Do not exceed 4 tablets in 24 hours. May cause drowsiness.',
        ),
        batch: const BatchModel(
          id: 'batch-101',
          batchNumber: 'PAR-2025-09',
          manufactureDate: '2025-06-01',
          expiryDate: '2027-06-01',
          quantity: 2000,
        ),
        scannedAt: DateTime.now().toIso8601String(),
        rawCode: codeData.isEmpty ? 'DATAMATRIX-PAR650-BATCH101-SN9988' : codeData,
        message: 'Authentic medicine verified.',
      );
    }

    _mockHistory.insert(0, result);
    return result;
  }

  @override
  Future<List<MedicineModel>> getMedicines() async {
    await Future.delayed(const Duration(milliseconds: 300));
    return const [
      MedicineModel(
        id: 'med-001',
        name: 'Paracetamol Extra',
        dosage: '650mg',
        manufacturer: 'Apex Pharma Global',
        description: 'Pain and fever relief.',
        storageInstructions: 'Store below 30°C.',
        warnings: 'Do not exceed recommended dose.',
      ),
      MedicineModel(
        id: 'med-002',
        name: 'Amoxicillin Trihydrate',
        dosage: '500mg',
        manufacturer: 'Astra Biotech Labs',
        description: 'Broad-spectrum antibiotic.',
        storageInstructions: 'Keep dry.',
        warnings: 'Penicillin allergy warning.',
      ),
    ];
  }

  @override
  Future<Map<String, dynamic>> sendAssistantQuery(String query) async {
    await Future.delayed(const Duration(milliseconds: 800));
    return {
      'session_id': 'session-mock-123',
      'response_text': 'I verified Paracetamol Extra 650mg. Dosage is 1 tablet every 6 hours as needed. Storage temperature should be under 30 degrees Celsius.',
      'audio_url': null,
    };
  }

  @override
  Future<List<VerificationResult>> getScanHistory() async {
    await Future.delayed(const Duration(milliseconds: 300));
    if (_mockHistory.isEmpty) {
      await verifyCode('DATAMATRIX-PAR650-BATCH101-SN9988');
    }
    return List.from(_mockHistory);
  }
}
