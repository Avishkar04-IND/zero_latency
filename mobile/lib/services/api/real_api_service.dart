import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../../core/config/api_config.dart';
import 'api_service.dart';
import '../../shared/models/verification_model.dart';
import '../../shared/models/medicine_model.dart';

class RealApiService implements ApiService {
  final String baseUrl;
  final String assistantUrl;
  final http.Client _client;

  RealApiService({
    String? baseUrl,
    String? assistantUrl,
    http.Client? client,
  })  : baseUrl = baseUrl ?? ApiConfig.baseUrl,
        assistantUrl = assistantUrl ?? ApiConfig.assistantUrl,
        _client = client ?? http.Client();

  @override
  Future<VerificationResult> verifyCode(String codeData, {double? lat, double? lng}) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/api/v1/verification/verify'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'code_data': codeData,
          'latitude': lat ?? 0.0,
          'longitude': lng ?? 0.0,
          'source': 'mobile_app',
        }),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final result = VerificationResult.fromJson(data);
        if (result.rawCode.isEmpty) {
          return VerificationResult(
            isValid: result.isValid,
            status: result.status,
            medicine: result.medicine,
            batch: result.batch,
            scannedAt: result.scannedAt,
            rawCode: codeData,
            message: result.message,
          );
        }
        return result;
      } else {
        String errorMsg = 'Server error during verification (${response.statusCode})';
        try {
          final data = jsonDecode(response.body) as Map<String, dynamic>;
          if (data.containsKey('detail')) {
            errorMsg = data['detail'].toString();
          } else if (data.containsKey('message')) {
            errorMsg = data['message'].toString();
          } else if (data.containsKey('error') && data['error'] is Map) {
            errorMsg = data['error']['message']?.toString() ?? errorMsg;
          }
        } catch (_) {}

        return VerificationResult(
          isValid: false,
          status: VerificationStatus.invalid,
          scannedAt: DateTime.now().toIso8601String(),
          rawCode: codeData,
          message: errorMsg,
        );
      }
    } on TimeoutException catch (_) {
      return VerificationResult(
        isValid: false,
        status: VerificationStatus.offlineError,
        scannedAt: DateTime.now().toIso8601String(),
        rawCode: codeData,
        message: 'Verification request timed out. Please check your internet connection.',
      );
    } on SocketException catch (_) {
      return VerificationResult(
        isValid: false,
        status: VerificationStatus.offlineError,
        scannedAt: DateTime.now().toIso8601String(),
        rawCode: codeData,
        message: 'Unable to connect to verification server. You appear to be offline.',
      );
    } on FormatException catch (_) {
      return VerificationResult(
        isValid: false,
        status: VerificationStatus.invalid,
        scannedAt: DateTime.now().toIso8601String(),
        rawCode: codeData,
        message: 'Malformed response received from verification server.',
      );
    } catch (e) {
      if (e is http.ClientException) {
        return VerificationResult(
          isValid: false,
          status: VerificationStatus.offlineError,
          scannedAt: DateTime.now().toIso8601String(),
          rawCode: codeData,
          message: 'Network error connecting to verification service: ${e.message}',
        );
      }
      return VerificationResult(
        isValid: false,
        status: VerificationStatus.offlineError,
        scannedAt: DateTime.now().toIso8601String(),
        rawCode: codeData,
        message: 'Network error connecting to verification service: $e',
      );
    }
  }

  @override
  Future<List<MedicineModel>> getMedicines() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/api/v1/medicines'),
      ).timeout(const Duration(seconds: 10));

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
      final response = await _client.post(
        Uri.parse('$assistantUrl/api/v1/assistant/query'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'session_id': 'mobile-session',
          'input_type': 'TEXT',
          'query_text': query,
        }),
      ).timeout(const Duration(seconds: 10));

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

