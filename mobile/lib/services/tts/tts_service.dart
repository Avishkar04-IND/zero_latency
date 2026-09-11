import 'package:flutter/foundation.dart';
import 'package:flutter_tts/flutter_tts.dart';

class TTSService {
  late FlutterTts _flutterTts;
  bool _isSpeaking = false;
  bool _isVoiceEnabled = true;
  double _speechRate = 0.5; // Normal rate for screen reader
  double _volume = 1.0;
  double _pitch = 1.0;

  bool get isSpeaking => _isSpeaking;
  double get speechRate => _speechRate;

  bool get isVoiceEnabled => _isVoiceEnabled;
  set isVoiceEnabled(bool enabled) {
    _isVoiceEnabled = enabled;
    if (!enabled) {
      stop();
    }
  }

  TTSService() {
    initTts();
  }

  void initTts() {
    try {
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
      _flutterTts.setLanguage("en-US").catchError((e) => debugPrint('TTS lang error: $e'));
      _flutterTts.setSpeechRate(_speechRate).catchError((e) => debugPrint('TTS rate error: $e'));
      _flutterTts.setVolume(_volume).catchError((e) => debugPrint('TTS vol error: $e'));
      _flutterTts.setPitch(_pitch).catchError((e) => debugPrint('TTS pitch error: $e'));
    } catch (e) {
      debugPrint('TTSService initialization warning: $e');
    }
  }

  Future<void> speak(String text) async {
    if (!_isVoiceEnabled || text.isEmpty) return;
    try {
      await stop();
      await _flutterTts.speak(text);
    } catch (e) {
      debugPrint('TTSService speak error: $e');
    }
  }

  Future<void> stop() async {
    _isSpeaking = false;
    try {
      await _flutterTts.stop();
    } catch (e) {
      debugPrint('TTSService stop error: $e');
    }
  }

  Future<void> setSpeechRate(double rate) async {
    _speechRate = rate;
    try {
      await _flutterTts.setSpeechRate(rate);
    } catch (e) {
      debugPrint('TTSService setSpeechRate error: $e');
    }
  }
}
