import 'medicine_model.dart';
import 'batch_model.dart';

enum VerificationStatus {
  authentic,
  expired,
  suspectedCounterfeit,
  recalled,
  revoked,
  invalid,
  offlineError,
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
      case 'VERIFIED':
        statusEnum = VerificationStatus.authentic;
        break;
      case 'EXPIRED':
        statusEnum = VerificationStatus.expired;
        break;
      case 'SUSPECTED_COUNTERFEIT':
      case 'SUSPICIOUS':
        statusEnum = VerificationStatus.suspectedCounterfeit;
        break;
      case 'RECALLED':
        statusEnum = VerificationStatus.recalled;
        break;
      case 'REVOKED':
        statusEnum = VerificationStatus.revoked;
        break;
      case 'OFFLINE_ERROR':
      case 'OFFLINE':
        statusEnum = VerificationStatus.offlineError;
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

  String toSpokenHeadline() {
    switch (status) {
      case VerificationStatus.authentic:
        return 'Medicine verified. ${medicine?.name ?? "Medicine"} ${medicine?.dosage ?? ""}.';
      case VerificationStatus.expired:
        return 'Warning. This medicine has expired. Expiry date was ${batch?.expiryDate ?? "unknown"}. Do not consume.';
      case VerificationStatus.suspectedCounterfeit:
        return 'Warning. This medicine appears suspicious. Do not rely on this verification.';
      case VerificationStatus.recalled:
        return 'Warning. This medicine batch has been recalled.';
      case VerificationStatus.revoked:
        return 'Warning. This medicine code has been revoked.';
      case VerificationStatus.offlineError:
        return 'Verification could not be completed because the service is unavailable offline.';
      case VerificationStatus.invalid:
      default:
        return 'This medicine code could not be verified.';
    }
  }

  String toSpokenResult() {
    return '${toSpokenHeadline()} ${medicine != null ? medicine!.toSpokenSummary() : ""}';
  }
}
