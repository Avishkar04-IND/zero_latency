import 'verification_model.dart';
import 'medicine_model.dart';
import 'batch_model.dart';

class HistoryRecord {
  final String id;
  final String medicineName;
  final VerificationStatus verificationStatus;
  final String timestamp;
  final String batchNumber;
  final String expiryDate;
  final String rawCode;
  final MedicineModel? medicine;
  final BatchModel? batch;
  final String message;

  const HistoryRecord({
    required this.id,
    required this.medicineName,
    required this.verificationStatus,
    required this.timestamp,
    required this.batchNumber,
    required this.expiryDate,
    required this.rawCode,
    this.medicine,
    this.batch,
    required this.message,
  });

  factory HistoryRecord.fromVerificationResult(VerificationResult result, {String? customId}) {
    final nowIso = DateTime.now().toIso8601String();
    final medName = result.medicine != null
        ? '${result.medicine!.name} ${result.medicine!.dosage}'.trim()
        : (result.rawCode.isNotEmpty ? result.rawCode : 'Scanned Code');

    return HistoryRecord(
      id: customId ?? 'hist_${DateTime.now().millisecondsSinceEpoch}',
      medicineName: medName,
      verificationStatus: result.status,
      timestamp: result.scannedAt.isNotEmpty ? result.scannedAt : nowIso,
      batchNumber: result.batch?.batchNumber ?? 'N/A',
      expiryDate: result.batch?.expiryDate ?? 'N/A',
      rawCode: result.rawCode,
      medicine: result.medicine,
      batch: result.batch,
      message: result.message,
    );
  }

  VerificationResult toVerificationResult() {
    return VerificationResult(
      isValid: verificationStatus == VerificationStatus.authentic,
      status: verificationStatus,
      medicine: medicine,
      batch: batch,
      scannedAt: timestamp,
      rawCode: rawCode,
      message: message,
    );
  }

  factory HistoryRecord.fromJson(Map<String, dynamic> json) {
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
      case 'SUSPECTEDCOUNTERFEIT':
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

    return HistoryRecord(
      id: json['id'] as String? ?? 'hist_${DateTime.now().millisecondsSinceEpoch}',
      medicineName: json['medicine_name'] as String? ?? 'Scanned Code',
      verificationStatus: statusEnum,
      timestamp: json['timestamp'] as String? ?? DateTime.now().toIso8601String(),
      batchNumber: json['batch_number'] as String? ?? 'N/A',
      expiryDate: json['expiry_date'] as String? ?? 'N/A',
      rawCode: json['raw_code'] as String? ?? '',
      medicine: json['medicine'] != null
          ? MedicineModel.fromJson(json['medicine'] as Map<String, dynamic>)
          : null,
      batch: json['batch'] != null
          ? BatchModel.fromJson(json['batch'] as Map<String, dynamic>)
          : null,
      message: json['message'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'medicine_name': medicineName,
      'verification_status': verificationStatus.name,
      'timestamp': timestamp,
      'batch_number': batchNumber,
      'expiry_date': expiryDate,
      'raw_code': rawCode,
      'medicine': medicine?.toJson(),
      'batch': batch?.toJson(),
      'message': message,
    };
  }

  String get formattedStatus {
    switch (verificationStatus) {
      case VerificationStatus.authentic:
        return 'Verified';
      case VerificationStatus.expired:
        return 'Expired';
      case VerificationStatus.suspectedCounterfeit:
        return 'Suspicious';
      case VerificationStatus.recalled:
        return 'Recalled';
      case VerificationStatus.revoked:
        return 'Revoked';
      case VerificationStatus.offlineError:
        return 'Offline';
      case VerificationStatus.invalid:
      default:
        return 'Invalid';
    }
  }

  String toSpokenHeadline() {
    return '$medicineName. $formattedStatus status.';
  }

  String toSpokenDetail() {
    final batchStr = batchNumber != 'N/A' ? 'Batch $batchNumber.' : '';
    final expStr = expiryDate != 'N/A' ? 'Expires $expiryDate.' : '';
    final timeStr = _formatReadableTimestamp(timestamp);
    return '$medicineName. $formattedStatus status. $batchStr $expStr Scanned $timeStr.';
  }

  static String _formatReadableTimestamp(String isoString) {
    try {
      final dt = DateTime.parse(isoString);
      final now = DateTime.now();
      final difference = now.difference(dt);

      String timeString = '${dt.hour > 12 ? dt.hour - 12 : (dt.hour == 0 ? 12 : dt.hour)}:${dt.minute.toString().padLeft(2, '0')} ${dt.hour >= 12 ? 'PM' : 'AM'}';

      if (difference.inDays == 0 && dt.day == now.day) {
        return 'today at $timeString';
      } else if (difference.inDays <= 1 && now.day - dt.day == 1) {
        return 'yesterday at $timeString';
      } else {
        return 'on ${dt.day}/${dt.month}/${dt.year} at $timeString';
      }
    } catch (_) {
      return isoString;
    }
  }
}
