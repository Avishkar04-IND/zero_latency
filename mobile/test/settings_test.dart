import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:smart_medicine_mobile/shared/models/app_settings.dart';
import 'package:smart_medicine_mobile/services/settings/settings_service.dart';
import 'package:smart_medicine_mobile/services/settings/local_settings_service.dart';
import 'package:smart_medicine_mobile/features/accessibility/settings/settings_controller.dart';
import 'package:smart_medicine_mobile/services/tts/tts_service.dart';
import 'package:smart_medicine_mobile/services/haptics/haptics_service.dart';

class MockTTSService extends TTSService {
  final List<String> spokenMessages = [];
  double _mockSpeechRate = 0.5;
  bool _mockVoiceEnabled = true;

  @override
  void initTts() {}

  @override
  bool get isVoiceEnabled => _mockVoiceEnabled;

  @override
  set isVoiceEnabled(bool enabled) {
    _mockVoiceEnabled = enabled;
  }

  @override
  double get speechRate => _mockSpeechRate;

  @override
  Future<void> setSpeechRate(double rate) async {
    _mockSpeechRate = rate;
  }

  @override
  Future<void> speak(String text, {bool queue = false}) async {
    if (!isVoiceEnabled || text.isEmpty) return;
    spokenMessages.add(text);
  }

  @override
  Future<void> stop() async {}
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('AppSettings Model Tests', () {
    test('Provides correct default values', () {
      const settings = AppSettings();

      expect(settings.voiceGuidanceEnabled, true);
      expect(settings.hapticsEnabled, true);
      expect(settings.speechSpeed, SpeechSpeed.normal);
      expect(settings.languageCode, 'en-US');
      expect(settings.speechRateValue, 0.5);
      expect(settings.speechSpeedLabel, 'Normal');
    });

    test('Maps speech speeds to correct speech rate values', () {
      const slow = AppSettings(speechSpeed: SpeechSpeed.slow);
      const fast = AppSettings(speechSpeed: SpeechSpeed.fast);
      const normal = AppSettings(speechSpeed: SpeechSpeed.normal);

      expect(slow.speechRateValue, 0.35);
      expect(fast.speechRateValue, 0.75);
      expect(normal.speechRateValue, 0.5);
    });

    test('Serializes and deserializes JSON cleanly', () {
      const original = AppSettings(
        voiceGuidanceEnabled: false,
        hapticsEnabled: false,
        speechSpeed: SpeechSpeed.fast,
        languageCode: 'en-US',
      );

      final json = original.toJson();
      final rehydrated = AppSettings.fromJson(json);

      expect(rehydrated.voiceGuidanceEnabled, false);
      expect(rehydrated.hapticsEnabled, false);
      expect(rehydrated.speechSpeed, SpeechSpeed.fast);
      expect(rehydrated.languageCode, 'en-US');
      expect(rehydrated, original);
    });

    test('Handles invalid or corrupted JSON safely without crashing', () {
      final corruptJson = {
        'voice_guidance_enabled': 'not_a_bool',
        'haptics_enabled': 12345,
        'speech_speed': 999,
        'language_code': null,
      };

      final parsed = AppSettings.fromJson(corruptJson);

      expect(parsed.voiceGuidanceEnabled, true);
      expect(parsed.hapticsEnabled, true);
      expect(parsed.speechSpeed, SpeechSpeed.normal);
      expect(parsed.languageCode, 'en-US');
    });
  });

  group('LocalSettingsService Tests', () {
    late SettingsService settingsService;
    late MockTTSService mockTTS;

    setUp(() {
      SharedPreferences.setMockInitialValues({});
      mockTTS = MockTTSService();
      settingsService = LocalSettingsService(ttsService: mockTTS);
    });

    test('Loads default settings on initial retrieval', () async {
      final settings = await settingsService.getSettings();

      expect(settings.voiceGuidanceEnabled, true);
      expect(settings.hapticsEnabled, true);
      expect(settings.speechSpeed, SpeechSpeed.normal);
    });

    test('Updates and persists settings changes', () async {
      const updated = AppSettings(
        voiceGuidanceEnabled: false,
        hapticsEnabled: true,
        speechSpeed: SpeechSpeed.slow,
      );

      await settingsService.updateSettings(updated);
      final retrieved = await settingsService.getSettings();

      expect(retrieved.voiceGuidanceEnabled, false);
      expect(retrieved.speechSpeed, SpeechSpeed.slow);
      expect(mockTTS.isVoiceEnabled, false);
    });

    test('Persists settings across fresh service instances', () async {
      const updated = AppSettings(
        voiceGuidanceEnabled: false,
        hapticsEnabled: false,
        speechSpeed: SpeechSpeed.fast,
        languageCode: 'en-US',
      );

      await settingsService.updateSettings(updated);

      final newMockTTS = MockTTSService();
      final freshService = LocalSettingsService(ttsService: newMockTTS);
      final reloaded = await freshService.getSettings();

      expect(reloaded.voiceGuidanceEnabled, false);
      expect(reloaded.hapticsEnabled, false);
      expect(reloaded.speechSpeed, SpeechSpeed.fast);
      expect(newMockTTS.isVoiceEnabled, false);
      expect(newMockTTS.speechRate, 0.75);
    });

    test('Resets settings back to default', () async {
      const custom = AppSettings(
        voiceGuidanceEnabled: false,
        hapticsEnabled: false,
        speechSpeed: SpeechSpeed.fast,
      );

      await settingsService.updateSettings(custom);
      await settingsService.resetSettings();

      final retrieved = await settingsService.getSettings();
      expect(retrieved.voiceGuidanceEnabled, true);
      expect(retrieved.hapticsEnabled, true);
      expect(retrieved.speechSpeed, SpeechSpeed.normal);
    });
  });

  group('SettingsController Tests', () {
    late LocalSettingsService settingsService;
    late MockTTSService mockTTS;
    late SettingsController controller;

    setUp(() {
      SharedPreferences.setMockInitialValues({});
      mockTTS = MockTTSService();
      settingsService = LocalSettingsService(ttsService: mockTTS);
      controller = SettingsController(
        settingsService: settingsService,
        ttsService: mockTTS,
      );
    });

    test('Loads initial settings and speaks greeting when requested', () async {
      await controller.loadSettings(speakInitial: true);

      expect(controller.state.isLoading, false);
      expect(controller.state.settings.voiceGuidanceEnabled, true);
      expect(mockTTS.spokenMessages.contains("Accessibility Settings menu active. Double tap items to adjust voice, haptics, or speech rate."), true);
    });

    test('Toggles voice guidance and updates TTS service state', () async {
      await controller.loadSettings(speakInitial: false);
      await controller.toggleVoiceGuidance(false);

      expect(controller.state.settings.voiceGuidanceEnabled, false);
      expect(mockTTS.isVoiceEnabled, false);
    });

    test('Toggles haptic vibrations and updates HapticsService flag', () async {
      await controller.loadSettings(speakInitial: false);
      await controller.toggleHaptics(false);

      expect(controller.state.settings.hapticsEnabled, false);
      expect(HapticsService.isHapticsEnabled, false);
    });

    test('Changes speech speed rate dynamically', () async {
      await controller.loadSettings(speakInitial: false);
      await controller.setSpeechSpeed(SpeechSpeed.fast);

      expect(controller.state.settings.speechSpeed, SpeechSpeed.fast);
      expect(mockTTS.speechRate, 0.75);
      expect(mockTTS.spokenMessages.contains("Speech rate set to fast speed."), true);
    });

    test('Resets settings to default and announces update', () async {
      await controller.loadSettings(speakInitial: false);
      await controller.setSpeechSpeed(SpeechSpeed.slow);
      await controller.resetToDefaults();

      expect(controller.state.settings.speechSpeed, SpeechSpeed.normal);
      expect(mockTTS.spokenMessages.contains("Settings reset to defaults."), true);
    });
  });
}
