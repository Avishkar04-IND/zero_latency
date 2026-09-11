import 'package:flutter/foundation.dart';
import '../../../services/tts/tts_service.dart';
import '../../../services/haptics/haptics_service.dart';
import '../../../services/settings/settings_service.dart';
import '../../../shared/models/app_settings.dart';

class SettingsState {
  final bool isLoading;
  final AppSettings settings;
  final String? errorMessage;

  const SettingsState({
    required this.isLoading,
    required this.settings,
    this.errorMessage,
  });

  factory SettingsState.initial() => const SettingsState(
        isLoading: true,
        settings: AppSettings(),
      );

  SettingsState copyWith({
    bool? isLoading,
    AppSettings? settings,
    String? errorMessage,
  }) {
    return SettingsState(
      isLoading: isLoading ?? this.isLoading,
      settings: settings ?? this.settings,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}

class SettingsController extends ValueNotifier<SettingsState> {
  final SettingsService settingsService;
  final TTSService ttsService;

  SettingsController({
    required this.settingsService,
    required this.ttsService,
  }) : super(SettingsState.initial());

  Future<void> loadSettings({bool speakInitial = false}) async {
    value = value.copyWith(isLoading: true, errorMessage: null);

    try {
      final loadedSettings = await settingsService.getSettings();
      ttsService.isVoiceEnabled = loadedSettings.voiceGuidanceEnabled;
      ttsService.setSpeechRate(loadedSettings.speechRateValue);
      HapticsService.isHapticsEnabled = loadedSettings.hapticsEnabled;

      value = value.copyWith(
        isLoading: false,
        settings: loadedSettings,
      );

      if (speakInitial) {
        ttsService.speak("Accessibility Settings menu active. Double tap items to adjust voice, haptics, or speech rate.");
      }
    } catch (e) {
      value = value.copyWith(
        isLoading: false,
        errorMessage: "Failed to load settings: $e",
      );
      HapticsService.error();
      ttsService.speak("Error loading accessibility settings.");
    }
  }

  Future<void> toggleVoiceGuidance(bool enabled) async {
    final updated = state.settings.copyWith(voiceGuidanceEnabled: enabled);
    await _updateSettingsInternal(updated);

    if (enabled) {
      ttsService.speak("Voice guidance enabled.");
    }
  }

  Future<void> toggleHaptics(bool enabled) async {
    final updated = state.settings.copyWith(hapticsEnabled: enabled);
    await _updateSettingsInternal(updated);

    HapticsService.scanningTick();
    ttsService.speak(enabled ? "Haptic vibrations enabled." : "Haptic vibrations disabled.");
  }

  Future<void> setSpeechSpeed(SpeechSpeed speed) async {
    final updated = state.settings.copyWith(speechSpeed: speed);
    await _updateSettingsInternal(updated);

    ttsService.setSpeechRate(updated.speechRateValue);
    HapticsService.scanningTick();

    final speedText = updated.speechSpeedLabel.toLowerCase();
    ttsService.speak("Speech rate set to $speedText speed.");
  }

  Future<void> setLanguage(String languageCode) async {
    final updated = state.settings.copyWith(languageCode: languageCode);
    await _updateSettingsInternal(updated);

    HapticsService.scanningTick();
    ttsService.speak("Language set to ${updated.languageDisplay}.");
  }

  Future<void> resetToDefaults() async {
    await settingsService.resetSettings();
    await loadSettings(speakInitial: false);

    HapticsService.codeDetected();
    ttsService.speak("Settings reset to defaults.");
  }

  Future<void> _updateSettingsInternal(AppSettings newSettings) async {
    try {
      await settingsService.updateSettings(newSettings);
      value = value.copyWith(settings: newSettings);
    } catch (e) {
      value = value.copyWith(errorMessage: "Failed to save settings: $e");
      HapticsService.error();
      ttsService.speak("Failed to save setting change.");
    }
  }

  SettingsState get state => value;
}
