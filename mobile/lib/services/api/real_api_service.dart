import 'dart:convert';
import 'package:http/http.dart' as http;
import 'api_service.dart';
import '../../shared/models/verification_model.dart';
import '../../shared/models/medicine_model.dart';

class RealApiService implements ApiService {
  final String baseUrl;
  final String assistantUrl;

  RealApiService({
    this.baseUrl = 'http://localhost:8000',
    this.assistantUrl = 'http://localhost:3000',
  });

  @override
  Future<VerificationResult> verifyCode(String codeData, {double? lat, double? lng}) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/verification/verify'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'code_data': codeData,
          'latitude': lat ?? 0.0,
          'longitude': lng ?? 0.0,
          'source': 'mobile_app',
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return VerificationResult.fromJson(data);
      } else {
        return VerificationResult(
          isValid: false,
          status: VerificationStatus.invalid,
          scannedAt: DateTime.now().toIso8601String(),
          rawCode: codeData,
          message: 'Server error during verification. Code: ${response.statusCode}',
        );
      }
    } catch (e) {
      return VerificationResult(
        isValid: false,
        status: VerificationStatus.invalid,
        scannedAt: DateTime.now().toIso8601String(),
        rawCode: codeData,
        message: 'Network error connecting to verification service: $e',
      );
    }
  }

  @override
  Future<List<MedicineModel>> getMedicines() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/v1/medicines'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final items = data['items'] as List? ?? [];
        return items.map((i) => MedicineModel.fromJson(i as Map<String, dynamic>)).toList();
      }
    } catch (_) {}
    return [];
  }

  @override
  Future<Map<String, dynamic>> sendAssistantQuery(String query) async {
    try {
      final response = await http.post(
        Uri.parse('$assistantUrl/api/v1/assistant/query'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'session_id': 'mobile-session',
          'input_type': 'TEXT',
          'query_text': query,
        }),
      );
      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      }
    } catch (_) {}
    return {'response_text': 'Unable to connect to Voice Assistant API.'};
  }

  @override
  Future<List<VerificationResult>> getScanHistory() async {
    return [];
  }
}
