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
    final upperCode = codeData.toUpperCase();

    if (upperCode.contains('EXPIRED') || upperCode.contains('EXP')) {
      result = VerificationResult(
        isValid: false,
        status: VerificationStatus.expired,
        medicine: const MedicineModel(
          id: 'med-002',
          name: 'Amoxicillin Trihydrate',
          genericName: 'Amoxicillin',
          dosage: '500mg',
          manufacturer: 'Astra Biotech Labs',
          description: 'Used for temporary relief of bacterial respiratory and urinary tract infections.',
          storageInstructions: 'Store below 25 degrees Celsius in a dry place.',
          warnings: 'Complete full prescribed course. Do not take if allergic to penicillin.',
        ),
        batch: const BatchModel(
          id: 'batch-987',
          batchNumber: 'AMX-2023-88',
          manufactureDate: '10 January 2023',
          expiryDate: '10 January 2024',
          quantity: 500,
        ),
        scannedAt: DateTime.now().toIso8601String(),
        rawCode: codeData,
        message: 'Warning. This medicine batch has expired.',
      );
    } else if (upperCode.contains('REVOKED') || upperCode.contains('REV')) {
      result = VerificationResult(
        isValid: false,
        status: VerificationStatus.revoked,
        medicine: const MedicineModel(
          id: 'med-003',
          name: 'Lipitor High-Potency',
          genericName: 'Atorvastatin Calcium',
          dosage: '20mg',
          manufacturer: 'BioPharma Global',
          description: 'Lipid-lowering agent for cardiovascular risk reduction.',
          storageInstructions: 'Store at 20°C to 25°C.',
          warnings: 'Batch revoked due to packaging seal inconsistency.',
        ),
        batch: const BatchModel(
          id: 'batch-303',
          batchNumber: 'LIP-2024-03',
          manufactureDate: '01 March 2024',
          expiryDate: '01 March 2026',
          quantity: 1200,
        ),
        scannedAt: DateTime.now().toIso8601String(),
        rawCode: codeData,
        message: 'Warning. This medicine code has been revoked.',
      );
    } else if (upperCode.contains('FAKE') || upperCode.contains('SUSPICIOUS') || upperCode.contains('COUNTERFEIT')) {
      result = VerificationResult(
        isValid: false,
        status: VerificationStatus.suspectedCounterfeit,
        scannedAt: DateTime.now().toIso8601String(),
        rawCode: codeData,
        message: 'Warning. This medicine code appears suspicious and is unverified.',
      );
    } else if (upperCode.contains('INVALID') || upperCode.contains('UNREADABLE')) {
      result = VerificationResult(
        isValid: false,
        status: VerificationStatus.invalid,
        scannedAt: DateTime.now().toIso8601String(),
        rawCode: codeData,
        message: 'This medicine code could not be verified.',
      );
    } else if (upperCode.contains('OFFLINE')) {
      result = VerificationResult(
        isValid: false,
        status: VerificationStatus.offlineError,
        scannedAt: DateTime.now().toIso8601String(),
        rawCode: codeData,
        message: 'Verification could not be completed because the service is unavailable offline.',
      );
    } else {
      result = VerificationResult(
        isValid: true,
        status: VerificationStatus.authentic,
        medicine: const MedicineModel(
          id: 'med-001',
          name: 'Paracetamol Extra',
          genericName: 'Acetaminophen',
          dosage: '650mg',
          manufacturer: 'Apex Pharma Global',
          description: 'Used for temporary relief of mild to moderate pain and fever.',
          storageInstructions: 'Store in a cool dry place below 30 degrees Celsius away from direct sunlight.',
          warnings: 'Follow the instructions on the packaging. Do not exceed 4 tablets in 24 hours.',
        ),
        batch: const BatchModel(
          id: 'batch-101',
          batchNumber: 'PAR-2025-09',
          manufactureDate: '11 September 2026',
          expiryDate: '10 September 2028',
          quantity: 2000,
        ),
        scannedAt: DateTime.now().toIso8601String(),
        rawCode: codeData.isEmpty ? 'DATAMATRIX-PAR650-BATCH101-SN9988' : codeData,
        message: 'Medicine verified. Authentic product.',
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
        genericName: 'Acetaminophen',
        dosage: '650mg',
        manufacturer: 'Apex Pharma Global',
        description: 'Pain and fever relief.',
        storageInstructions: 'Store below 30°C.',
        warnings: 'Do not exceed recommended dose.',
      ),
      MedicineModel(
        id: 'med-002',
        name: 'Amoxicillin Trihydrate',
        genericName: 'Amoxicillin',
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
