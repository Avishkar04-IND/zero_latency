import 'scanner_state.dart';

class ScannerGuidanceEngine {
  static DateTime _lastSpokenTime = DateTime.fromMillisecondsSinceEpoch(0);
  static GuidanceDirection _lastDirection = GuidanceDirection.none;
  static ScannerStatus _lastStatus = ScannerStatus.initializing;
  static const int throttleDurationMs = 2800; // Throttle TTS guidance every 2.8 seconds

  static String getGuidanceMessage(ScannerState state) {
    switch (state.status) {
      case ScannerStatus.initializing:
        return "Initializing camera scanner...";
      case ScannerStatus.cameraPermissionDenied:
        return "Camera access is required to scan your medicine code.";
      case ScannerStatus.codeDetected:
      case ScannerStatus.capturing:
        return "Medicine code detected. Hold steady.";
      case ScannerStatus.verifying:
        return "Verifying medicine code with database...";
      case ScannerStatus.verificationResult:
        return "Verification complete.";
      case ScannerStatus.cameraError:
      case ScannerStatus.scannerError:
        return "Scanner error encountered. Tap retry to restart.";
      case ScannerStatus.offlineError:
        return "Code detected, but verification is unavailable right now. Please check network connection.";
      case ScannerStatus.positionGuidance:
        return _getDirectionText(state.guidanceDirection);
      case ScannerStatus.searching:
      case ScannerStatus.ready:
      default:
        return "Searching for medicine DataMatrix or QR code.";
    }
  }

  static String _getDirectionText(GuidanceDirection direction) {
    switch (direction) {
      case GuidanceDirection.tooFar:
        return "Move phone closer to medicine package.";
      case GuidanceDirection.tooClose:
        return "Move phone slightly farther away.";
      case GuidanceDirection.moveLeft:
        return "Move camera slightly left.";
      case GuidanceDirection.moveRight:
        return "Move camera slightly right.";
      case GuidanceDirection.moveUp:
        return "Move camera slightly up.";
      case GuidanceDirection.moveDown:
        return "Move camera slightly down.";
      case GuidanceDirection.holdSteady:
        return "Hold steady. Code detected.";
      case GuidanceDirection.none:
      default:
        return "Searching for code.";
    }
  }

  /// Determines if a guidance prompt should be spoken based on priority & throttling
  static bool shouldSpeakGuidance(ScannerState state) {
    final now = DateTime.now();

    // High Priority Statuses (Always speak immediately)
    if (state.status == ScannerStatus.codeDetected ||
        state.status == ScannerStatus.verifying ||
        state.status == ScannerStatus.cameraPermissionDenied ||
        state.status == ScannerStatus.offlineError) {
      if (_lastStatus != state.status) {
        _lastStatus = state.status;
        _lastSpokenTime = now;
        return true;
      }
    }

    // Guidance Direction Throttling
    if (state.status == ScannerStatus.positionGuidance || state.status == ScannerStatus.searching) {
      final elapsed = now.difference(_lastSpokenTime).inMilliseconds;
      if (elapsed >= throttleDurationMs || _lastDirection != state.guidanceDirection) {
        _lastSpokenTime = now;
        _lastDirection = state.guidanceDirection;
        _lastStatus = state.status;
        return true;
      }
    }

    return false;
  }
}
