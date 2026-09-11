import 'package:flutter/foundation.dart';
import '../../../services/tts/tts_service.dart';
import '../../../services/haptics/haptics_service.dart';
import '../../../services/history/history_service.dart';
import '../../../shared/models/history_record.dart';

class HistoryState {
  final bool isLoading;
  final List<HistoryRecord> records;
  final String? errorMessage;
  final String? deleteConfirmationId;
  final bool isClearAllConfirming;

  const HistoryState({
    required this.isLoading,
    required this.records,
    this.errorMessage,
    this.deleteConfirmationId,
    this.isClearAllConfirming = false,
  });

  factory HistoryState.initial() => const HistoryState(
        isLoading: true,
        records: [],
      );

  HistoryState copyWith({
    bool? isLoading,
    List<HistoryRecord>? records,
    String? errorMessage,
    String? deleteConfirmationId,
    bool? isClearAllConfirming,
    bool clearDeleteConfirmation = false,
  }) {
    return HistoryState(
      isLoading: isLoading ?? this.isLoading,
      records: records ?? this.records,
      errorMessage: errorMessage ?? this.errorMessage,
      deleteConfirmationId: clearDeleteConfirmation
          ? null
          : (deleteConfirmationId ?? this.deleteConfirmationId),
      isClearAllConfirming: isClearAllConfirming ?? this.isClearAllConfirming,
    );
  }
}

class HistoryController extends ValueNotifier<HistoryState> {
  final HistoryService historyService;
  final TTSService ttsService;

  HistoryController({
    required this.historyService,
    required this.ttsService,
  }) : super(HistoryState.initial());

  Future<void> loadHistory({bool speakSummary = true}) async {
    value = value.copyWith(isLoading: true, errorMessage: null);

    try {
      final records = await historyService.getHistoryRecords();
      value = value.copyWith(
        isLoading: false,
        records: records,
      );

      if (speakSummary) {
        if (records.isEmpty) {
          ttsService.speak("You have no scan history yet.");
        } else {
          final countStr = records.length == 1 ? "1 scan record" : "${records.length} scan records";
          ttsService.speak("Scan History. You have $countStr. Swipe or tap items to hear details.");
        }
      }
    } catch (e) {
      value = value.copyWith(
        isLoading: false,
        errorMessage: "Failed to load scan history: $e",
      );
      HapticsService.error();
      ttsService.speak("Error loading scan history.");
    }
  }

  void speakCurrentSummary() {
    if (state.records.isEmpty) {
      ttsService.speak("You have no scan history yet.");
    } else {
      ttsService.speak("Scan History contains ${state.records.length} records. Newest scans are listed first.");
    }
  }

  void speakItemDetails(HistoryRecord record) {
    HapticsService.scanningTick();
    ttsService.speak(record.toSpokenDetail());
  }

  void requestDeleteConfirmation(String id) {
    final record = state.records.firstWhere(
      (r) => r.id == id,
      orElse: () => HistoryRecord(
        id: id,
        medicineName: 'Scan item',
        verificationStatus: state.records.first.verificationStatus,
        timestamp: '',
        batchNumber: '',
        expiryDate: '',
        rawCode: '',
        message: '',
      ),
    );

    value = value.copyWith(deleteConfirmationId: id);
    HapticsService.expiredWarning();
    ttsService.speak("Delete scan for ${record.medicineName} from history? Double tap to confirm deletion.");
  }

  void cancelDeleteConfirmation() {
    value = value.copyWith(clearDeleteConfirmation: true);
    ttsService.speak("Deletion cancelled.");
  }

  Future<void> confirmAndDelete(String id) async {
    try {
      await historyService.deleteRecord(id);
      value = value.copyWith(clearDeleteConfirmation: true);
      await HapticsService.codeDetected();
      ttsService.speak("Scan record deleted.");
      await loadHistory(speakSummary: false);
    } catch (e) {
      value = value.copyWith(
        clearDeleteConfirmation: true,
        errorMessage: "Failed to delete record: $e",
      );
      HapticsService.error();
      ttsService.speak("Failed to delete record.");
    }
  }

  void requestClearAllConfirmation() {
    if (state.records.isEmpty) {
      ttsService.speak("History is already empty.");
      return;
    }

    value = value.copyWith(isClearAllConfirming: true);
    HapticsService.suspiciousAlert();
    ttsService.speak("Are you sure you want to clear all scan history? This action cannot be undone. Double tap to confirm.");
  }

  void cancelClearAllConfirmation() {
    value = value.copyWith(isClearAllConfirming: false);
    ttsService.speak("Clear history cancelled.");
  }

  Future<void> confirmAndClearAll() async {
    try {
      await historyService.clearHistory();
      value = value.copyWith(isClearAllConfirming: false);
      await HapticsService.codeDetected();
      ttsService.speak("All scan history cleared.");
      await loadHistory(speakSummary: false);
    } catch (e) {
      value = value.copyWith(
        isClearAllConfirming: false,
        errorMessage: "Failed to clear history: $e",
      );
      HapticsService.error();
      ttsService.speak("Failed to clear history.");
    }
  }

  HistoryState get state => value;
}
