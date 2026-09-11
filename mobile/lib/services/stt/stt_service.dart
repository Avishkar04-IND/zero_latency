import 'package:flutter/foundation.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;

class STTService {
  late stt.SpeechToText _speech;
  bool _isAvailable = false;
  bool _isListening = false;

  bool get isListening => _isListening;
  bool get isAvailable => _isAvailable;

  STTService() {
    _speech = stt.SpeechToText();
  }

  Future<bool> initialize() async {
    _isAvailable = await _speech.initialize(
      onError: (val) => debugPrint('STT onError: $val'),
      onStatus: (val) {
        debugPrint('STT onStatus: $val');
        if (val == 'done' || val == 'notListening') {
          _isListening = false;
        }
      },
    );
    return _isAvailable;
  }

  Future<void> listen({required Function(String text) onResult}) async {
    if (!_isAvailable) {
      final available = await initialize();
      if (!available) return;
    }
    _isListening = true;
    await _speech.listen(
      onResult: (val) {
        if (val.recognizedWords.isNotEmpty) {
          onResult(val.recognizedWords);
        }
      },
      listenFor: const Duration(seconds: 10),
      pauseFor: const Duration(seconds: 3),
    );
  }

  Future<void> stop() async {
    await _speech.stop();
    _isListening = false;
  }
}
