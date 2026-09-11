import '../../shared/models/verification_model.dart';
import '../../shared/models/medicine_model.dart';

abstract class ApiService {
  Future<VerificationResult> verifyCode(String codeData, {double? lat, double? lng});
  Future<List<MedicineModel>> getMedicines();
  Future<Map<String, dynamic>> sendAssistantQuery(String query);
  Future<List<VerificationResult>> getScanHistory();
}
