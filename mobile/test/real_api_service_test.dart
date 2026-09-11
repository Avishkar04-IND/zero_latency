import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:smart_medicine_mobile/services/api/real_api_service.dart';
import 'package:smart_medicine_mobile/shared/models/verification_model.dart';

void main() {
  group('RealApiService Verification Tests', () {
    test('1. AUTHENTIC response parsing for code MD110', () async {
      final mockClient = MockClient((request) async {
        expect(request.url.path, '/api/v1/verification/verify');
        final body = jsonDecode(request.body) as Map<String, dynamic>;
        expect(body['code_data'], 'MD110');
        expect(body['source'], 'mobile_app');

        return http.Response(
          jsonEncode({
            "is_valid": true,
            "verification_status": "AUTHENTIC",
            "scanned_at": "2026-09-11T12:00:00Z",
            "raw_code": "MD110",
            "message": "Medicine verified successfully as authentic.",
            "medicine": {
              "id": "med-110",
              "name": "Paracetamol 500mg",
              "generic_name": "Acetaminophen",
              "dosage": "500mg",
              "manufacturer": "Pharma Corp",
              "description": "Pain reliever",
              "storage_instructions": "Store below 25C",
              "warnings": "Do not exceed recommended dose"
            },
            "batch": {
              "id": "batch-110",
              "batch_number": "B12345",
              "manufacture_date": "2025-01-01",
              "expiry_date": "2027-12-31",
              "quantity": 100
            }
          }),
          200,
          headers: {'content-type': 'application/json'},
        );
      });

      final apiService = RealApiService(baseUrl: 'http://test-server:8000', client: mockClient);
      final result = await apiService.verifyCode('MD110');

      expect(result.isValid, isTrue);
      expect(result.status, VerificationStatus.authentic);
      expect(result.rawCode, 'MD110');
      expect(result.medicine, isNotNull);
      expect(result.medicine!.name, 'Paracetamol 500mg');
      expect(result.medicine!.genericName, 'Acetaminophen');
      expect(result.batch, isNotNull);
      expect(result.batch!.batchNumber, 'B12345');
    });

    test('2. INVALID response parsing for unknown code', () async {
      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode({
            "is_valid": false,
            "verification_status": "INVALID",
            "message": "Unknown or invalid medicine code.",
            "medicine": null,
            "batch": null
          }),
          200,
          headers: {'content-type': 'application/json'},
        );
      });

      final apiService = RealApiService(baseUrl: 'http://test-server:8000', client: mockClient);
      final result = await apiService.verifyCode('UNKNOWN_999');

      expect(result.isValid, isFalse);
      expect(result.status, VerificationStatus.invalid);
      expect(result.message, contains('Unknown or invalid'));
      expect(result.medicine, isNull);
    });

    test('3. EXPIRED response parsing', () async {
      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode({
            "is_valid": false,
            "verification_status": "EXPIRED",
            "message": "Warning. Medicine batch has expired.",
            "medicine": {
              "name": "Amoxicillin 500mg",
              "dosage": "500mg",
              "manufacturer": "Bio Labs",
              "description": "Antibiotic",
              "storage_instructions": "Keep cool",
              "warnings": "Expired"
            },
            "batch": {
              "batch_number": "EXP-2023",
              "manufacture_date": "2022-01-01",
              "expiry_date": "2023-01-01"
            }
          }),
          200,
          headers: {'content-type': 'application/json'},
        );
      });

      final apiService = RealApiService(baseUrl: 'http://test-server:8000', client: mockClient);
      final result = await apiService.verifyCode('EXPIRED_CODE');

      expect(result.isValid, isFalse);
      expect(result.status, VerificationStatus.expired);
      expect(result.batch!.expiryDate, '2023-01-01');
    });

    test('4. Malformed response handling', () async {
      final mockClient = MockClient((request) async {
        return http.Response('Internal error html page', 200);
      });

      final apiService = RealApiService(baseUrl: 'http://test-server:8000', client: mockClient);
      final result = await apiService.verifyCode('MD110');

      expect(result.isValid, isFalse);
      expect(result.status, VerificationStatus.invalid);
      expect(result.message, contains('Malformed response'));
    });

    test('5. HTTP error (400 Bad Request) handling', () async {
      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode({"detail": "Invalid QR format payload"}),
          400,
          headers: {'content-type': 'application/json'},
        );
      });

      final apiService = RealApiService(baseUrl: 'http://test-server:8000', client: mockClient);
      final result = await apiService.verifyCode('BAD_FORMAT');

      expect(result.isValid, isFalse);
      expect(result.status, VerificationStatus.invalid);
      expect(result.message, 'Invalid QR format payload');
    });

    test('6. Network connection failure handling', () async {
      final mockClient = MockClient((request) async {
        throw http.ClientException('Failed to connect to host');
      });

      final apiService = RealApiService(baseUrl: 'http://test-server:8000', client: mockClient);
      final result = await apiService.verifyCode('MD110');

      expect(result.isValid, isFalse);
      expect(result.status, VerificationStatus.offlineError);
      expect(result.message, contains('Network error connecting to verification service'));
    });
  });
}
