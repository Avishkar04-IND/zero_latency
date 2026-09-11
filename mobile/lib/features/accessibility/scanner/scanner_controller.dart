import 'package:flutter/foundation.dart';
import '../../../services/tts/tts_service.dart';
import '../../../services/haptics/haptics_service.dart';
import '../../../services/api/api_service.dart';
import '../../../shared/models/verification_model.dart';
import '../../../services/history/history_service.dart';
import 'scanner_state.dart';
import 'scanner_guidance.dart';

class ScannerController extends ValueNotifier<ScannerState> {
  final TTSService ttsService;
  final ApiService apiService;
  final HistoryService? historyService;

  bool _isDisposed = false;

  ScannerController({
    required this.ttsService,
    required this.apiService,
    this.historyService,
  }) : super(ScannerState.initial());

  Future<void> initializeScanner() async {
    _updateState(state.copyWith(status: ScannerStatus.initializing));
    await Future.delayed(const Duration(milliseconds: 400));
    _updateState(state.copyWith(status: ScannerStatus.searching));
    _triggerGuidanceVoice();
    HapticsService.scannerStarted();
  }

  void onBarcodeDetected(String rawCode, {String codeFormat = 'DATAMATRIX'}) async {
    if (state.isProcessing || state.status == ScannerStatus.codeDetected || state.status == ScannerStatus.verifying) {
      return; // Lock against duplicate detection
    }

    _updateState(state.copyWith(
      status: ScannerStatus.codeDetected,
      scannedCode: rawCode,
      codeFormat: codeFormat,
      isProcessing: true,
      guidanceDirection: GuidanceDirection.holdSteady,
    ));

    await HapticsService.codeDetected();
    ttsService.speak("Medicine code detected. Hold steady.");

    await Future.delayed(const Duration(milliseconds: 800));
    await verifyScannedCode(rawCode);
  }

  Future<void> verifyScannedCode(String codeData) async {
    _updateState(state.copyWith(
      status: ScannerStatus.verifying,
      isProcessing: true,
    ));

    await HapticsService.verificationStarted();
    ttsService.speak("Verifying medicine code with server.");

    try {
      final result = await apiService.verifyCode(codeData);

      try {
        await historyService?.saveVerification(result);
      } catch (e) {
        debugPrint("ScannerController: Failed to save scan history: $e");
      }

      if (_isDisposed) return;

      _updateState(state.copyWith(
        status: ScannerStatus.verificationResult,
        verificationResult: result,
        isProcessing: false,
      ));

      if (result.status == VerificationStatus.authentic) {
        await HapticsService.verifiedAuthentic();
      } else if (result.status == VerificationStatus.expired) {
        await HapticsService.expiredWarning();
      } else if (result.status == VerificationStatus.suspectedCounterfeit) {
        await HapticsService.suspiciousAlert();
      } else {
        await HapticsService.invalidCode();
      }
    } catch (e) {
      if (_isDisposed) return;
      _updateState(state.copyWith(
        status: ScannerStatus.verificationError,
        errorMessage: "Failed to verify medicine code: $e",
        isProcessing: false,
      ));
      await HapticsService.error();
      ttsService.speak("Verification error encountered.");
    }
  }

  void updatePositionGuidance(GuidanceDirection direction) {
    if (state.isProcessing || state.status == ScannerStatus.codeDetected) return;

    _updateState(state.copyWith(
      status: ScannerStatus.positionGuidance,
      guidanceDirection: direction,
    ));

    _triggerGuidanceVoice();
  }

  void toggleTorch() {
    final nextTorch = !state.isTorchOn;
    _updateState(state.copyWith(isTorchOn: nextTorch));
    HapticsService.scanningTick();
    ttsService.speak(nextTorch ? "Flashlight turned on." : "Flashlight turned off.");
  }

  void setPermissionDenied() {
    _updateState(state.copyWith(
      status: ScannerStatus.cameraPermissionDenied,
      errorMessage: "Camera permission denied.",
    ));
    ttsService.speak("Camera access is required to scan your medicine code.");
  }

  void _triggerGuidanceVoice() {
    if (ScannerGuidanceEngine.shouldSpeakGuidance(state)) {
      final msg = ScannerGuidanceEngine.getGuidanceMessage(state);
      ttsService.speak(msg);
    }
  }

  void _updateState(ScannerState newState) {
    if (!_isDisposed) {
      value = newState;
    }
  }

  ScannerState get state => value;

  @override
  void dispose() {
    _isDisposed = true;
    super.dispose();
  }
}
