import 'medicine_model.dart';
import 'batch_model.dart';

enum VerificationStatus {
  authentic,
  expired,
  suspectedCounterfeit,
  recalled,
  invalid,
}

class VerificationResult {
  final bool isValid;
  final VerificationStatus status;
  final MedicineModel? medicine;
  final BatchModel? batch;
  final String scannedAt;
  final String rawCode;
  final String message;

  const VerificationResult({
    required this.isValid,
    required this.status,
    this.medicine,
    this.batch,
    required this.scannedAt,
    required this.rawCode,
    required this.message,
  });

  factory VerificationResult.fromJson(Map<String, dynamic> json) {
    final statusStr = json['verification_status'] as String? ?? 'INVALID';
    VerificationStatus statusEnum;
    switch (statusStr.toUpperCase()) {
      case 'AUTHENTIC':
        statusEnum = VerificationStatus.authentic;
        break;
      case 'EXPIRED':
        statusEnum = VerificationStatus.expired;
        break;
      case 'SUSPECTED_COUNTERFEIT':
        statusEnum = VerificationStatus.suspectedCounterfeit;
        break;
      case 'RECALLED':
        statusEnum = VerificationStatus.recalled;
        break;
      default:
        statusEnum = VerificationStatus.invalid;
    }

    return VerificationResult(
      isValid: json['is_valid'] as bool? ?? false,
      status: statusEnum,
      medicine: json['medicine'] != null
          ? MedicineModel.fromJson(json['medicine'] as Map<String, dynamic>)
          : null,
      batch: json['batch'] != null
          ? BatchModel.fromJson(json['batch'] as Map<String, dynamic>)
          : null,
      scannedAt: json['scanned_at'] as String? ?? DateTime.now().toIso8601String(),
      rawCode: json['raw_code'] as String? ?? '',
      message: json['message'] as String? ?? '',
    );
  }

  String toSpokenResult() {
    switch (status) {
      case VerificationStatus.authentic:
        return 'Verified Authentic. Medicine: ${medicine?.name ?? "Unknown"}. Dosage: ${medicine?.dosage ?? "Unknown"}. Expiry Date: ${batch?.expiryDate ?? "Unknown"}.';
      case VerificationStatus.expired:
        return 'Warning! Medicine is EXPIRED. Expiry Date was ${batch?.expiryDate ?? "Unknown"}. Do not consume.';
      case VerificationStatus.suspectedCounterfeit:
        return 'ALERT! Suspected Counterfeit Code. This medicine code could not be verified in the database.';
      case VerificationStatus.recalled:
        return 'ALERT! Recalled Medicine Batch. Do not consume this medicine.';
      case VerificationStatus.invalid:
      default:
        return 'Invalid or Unreadable Code scanned. Please scan again.';
    }
  }
}
