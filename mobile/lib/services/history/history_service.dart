import '../../shared/models/history_record.dart';
import '../../shared/models/verification_model.dart';

abstract class HistoryService {
  Future<List<HistoryRecord>> getHistoryRecords();
  Future<void> saveRecord(HistoryRecord record);
  Future<void> saveVerification(VerificationResult result);
  Future<void> deleteRecord(String id);
  Future<void> clearHistory();
}
