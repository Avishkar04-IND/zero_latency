import 'package:flutter/foundation.dart';
import 'package:flutter_tts/flutter_tts.dart';

class TTSService {
  late FlutterTts _flutterTts;
  bool _isSpeaking = false;
  bool isVoiceEnabled = true;
  double _speechRate = 0.5; // Normal rate for screen reader
  double _volume = 1.0;
  double _pitch = 1.0;

  bool get isSpeaking => _isSpeaking;
  double get speechRate => _speechRate;

  TTSService() {
    _initTts();
  }

  void _initTts() {
    _flutterTts = FlutterTts();
    _flutterTts.setStartHandler(() {
      _isSpeaking = true;
    });
    _flutterTts.setCompletionHandler(() {
      _isSpeaking = false;
    });
    _flutterTts.setErrorHandler((msg) {
      _isSpeaking = false;
      debugPrint('TTS Error: $msg');
    });
    _flutterTts.setLanguage("en-US");
    _flutterTts.setSpeechRate(_speechRate);
    _flutterTts.setVolume(_volume);
    _flutterTts.setPitch(_pitch);
  }

  Future<void> speak(String text) async {
    if (!isVoiceEnabled || text.isEmpty) return;
    await stop();
    await _flutterTts.speak(text);
  }

  Future<void> stop() async {
    await _flutterTts.stop();
    _isSpeaking = false;
  }

  Future<void> setSpeechRate(double rate) async {
    _speechRate = rate;
    await _flutterTts.setSpeechRate(rate);
  }
}
