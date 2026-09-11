import 'package:vibration/vibration.dart';

class HapticsService {
  static Future<bool> _hasVibrator() async {
    try {
      return (await Vibration.hasVibrator()) ?? false;
    } catch (_) {
      return false;
    }
  }

  /// Light tick when scanning active / searching
  static Future<void> scanningTick() async {
    if (await _hasVibrator()) {
      Vibration.vibrate(duration: 40, amplitude: 50);
    }
  }

  /// Pulse when camera detects a DataMatrix / QR boundary
  static Future<void> codeDetected() async {
    if (await _hasVibrator()) {
      Vibration.vibrate(pattern: [0, 80, 50, 80]);
    }
  }

  /// Quick snap when image / code frame is captured
  static Future<void> capture() async {
    if (await _hasVibrator()) {
      Vibration.vibrate(duration: 100, amplitude: 180);
    }
  }

  /// Strong, unmistakable double-heavy pulse on successful authentic verification
  static Future<void> verifiedAuthentic() async {
    if (await _hasVibrator()) {
      // 0ms delay, 150ms heavy pulse, 100ms gap, 300ms strong pulse
      Vibration.vibrate(pattern: [0, 150, 100, 300], intensities: [0, 255, 0, 255]);
    }
  }

  /// Triple sharp burst for expired medicine warning
  static Future<void> expiredWarning() async {
    if (await _hasVibrator()) {
      Vibration.vibrate(pattern: [0, 100, 80, 100, 80, 250]);
    }
  }

  /// Long continuous heavy alarm vibration for counterfeit / recall alert
  static Future<void> suspiciousAlert() async {
    if (await _hasVibrator()) {
      Vibration.vibrate(pattern: [0, 500, 100, 500], intensities: [0, 255, 0, 255]);
    }
  }

  /// Short double buzz for invalid code / unreadable frame
  static Future<void> invalidCode() async {
    if (await _hasVibrator()) {
      Vibration.vibrate(pattern: [0, 80, 80, 80]);
    }
  }

  /// Error vibration
  static Future<void> error() async {
    if (await _hasVibrator()) {
      Vibration.vibrate(pattern: [0, 200, 100, 200]);
    }
  }
}
