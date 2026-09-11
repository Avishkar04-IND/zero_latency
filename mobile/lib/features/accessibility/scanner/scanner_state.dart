import '../../../shared/models/verification_model.dart';

enum ScannerStatus {
  initializing,
  ready,
  searching,
  positionGuidance,
  codeDetected,
  capturing,
  verifying,
  verificationResult,
  cameraPermissionDenied,
  cameraError,
  scannerError,
  noCodeFound,
  verificationError,
  offlineError,
}

enum GuidanceDirection {
  tooFar,
  tooClose,
  moveLeft,
  moveRight,
  moveUp,
  moveDown,
  holdSteady,
  none,
}

class ScannerState {
  final ScannerStatus status;
  final GuidanceDirection guidanceDirection;
  final String? scannedCode;
  final String? codeFormat;
  final VerificationResult? verificationResult;
  final String? errorMessage;
  final bool isTorchOn;
  final bool isProcessing;

  const ScannerState({
    required this.status,
    this.guidanceDirection = GuidanceDirection.none,
    this.scannedCode,
    this.codeFormat,
    this.verificationResult,
    this.errorMessage,
    this.isTorchOn = false,
    this.isProcessing = false,
  });

  factory ScannerState.initial() {
    return const ScannerState(status: ScannerStatus.initializing);
  }

  ScannerState copyWith({
    ScannerStatus? status,
    GuidanceDirection? guidanceDirection,
    String? scannedCode,
    String? codeFormat,
    VerificationResult? verificationResult,
    String? errorMessage,
    bool? isTorchOn,
    bool? isProcessing,
  }) {
    return ScannerState(
      status: status ?? this.status,
      guidanceDirection: guidanceDirection ?? this.guidanceDirection,
      scannedCode: scannedCode ?? this.scannedCode,
      codeFormat: codeFormat ?? this.codeFormat,
      verificationResult: verificationResult ?? this.verificationResult,
      errorMessage: errorMessage ?? this.errorMessage,
      isTorchOn: isTorchOn ?? this.isTorchOn,
      isProcessing: isProcessing ?? this.isProcessing,
    );
  }
}
