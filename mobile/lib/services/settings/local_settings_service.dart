import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'settings_service.dart';
import '../../shared/models/app_settings.dart';
import '../haptics/haptics_service.dart';
import '../tts/tts_service.dart';

class LocalSettingsService implements SettingsService {
  static const String _storageKey = 'zero_latency_accessibility_settings_v1';

  AppSettings _currentSettings = const AppSettings();
  bool _isLoaded = false;
  final TTSService? ttsService;

  LocalSettingsService({this.ttsService});

  Future<void> _ensureLoaded() async {
    if (_isLoaded) return;
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonString = prefs.getString(_storageKey);
      if (jsonString != null && jsonString.isNotEmpty) {
        final Map<String, dynamic> decoded = jsonDecode(jsonString);
        _currentSettings = AppSettings.fromJson(decoded);
      }
    } catch (e) {
      debugPrint("LocalSettingsService warning: failed to load settings from storage: $e");
      _currentSettings = const AppSettings();
    } finally {
      _isLoaded = true;
      _applyToServices(_currentSettings);
    }
  }

  void _applyToServices(AppSettings settings) {
    HapticsService.isHapticsEnabled = settings.hapticsEnabled;
    if (ttsService != null) {
      ttsService!.isVoiceEnabled = settings.voiceGuidanceEnabled;
      ttsService!.setSpeechRate(settings.speechRateValue);
    }
  }

  @override
  Future<AppSettings> getSettings() async {
    await _ensureLoaded();
    return _currentSettings;
  }

  @override
  Future<void> updateSettings(AppSettings settings) async {
    await _ensureLoaded();
    _currentSettings = settings;
    _applyToServices(_currentSettings);

    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonString = jsonEncode(settings.toJson());
      await prefs.setString(_storageKey, jsonString);
    } catch (e) {
      debugPrint("LocalSettingsService warning: failed to save settings: $e");
    }
  }

  @override
  Future<void> resetSettings() async {
    await updateSettings(const AppSettings());
  }
}
