enum SpeechSpeed {
  slow,
  normal,
  fast,
}

class AppSettings {
  final bool voiceGuidanceEnabled;
  final bool hapticsEnabled;
  final SpeechSpeed speechSpeed;
  final String languageCode;

  const AppSettings({
    this.voiceGuidanceEnabled = true,
    this.hapticsEnabled = true,
    this.speechSpeed = SpeechSpeed.normal,
    this.languageCode = 'en-US',
  });

  double get speechRateValue {
    switch (speechSpeed) {
      case SpeechSpeed.slow:
        return 0.35;
      case SpeechSpeed.fast:
        return 0.75;
      case SpeechSpeed.normal:
      default:
        return 0.5;
    }
  }

  String get speechSpeedLabel {
    switch (speechSpeed) {
      case SpeechSpeed.slow:
        return 'Slow';
      case SpeechSpeed.fast:
        return 'Fast';
      case SpeechSpeed.normal:
      default:
        return 'Normal';
    }
  }

  String get languageDisplay {
    switch (languageCode) {
      case 'en-US':
      default:
        return 'English (United States)';
    }
  }

  AppSettings copyWith({
    bool? voiceGuidanceEnabled,
    bool? hapticsEnabled,
    SpeechSpeed? speechSpeed,
    String? languageCode,
  }) {
    return AppSettings(
      voiceGuidanceEnabled: voiceGuidanceEnabled ?? this.voiceGuidanceEnabled,
      hapticsEnabled: hapticsEnabled ?? this.hapticsEnabled,
      speechSpeed: speechSpeed ?? this.speechSpeed,
      languageCode: languageCode ?? this.languageCode,
    );
  }

  factory AppSettings.fromJson(Map<String, dynamic> json) {
    final speedStr = json['speech_speed'] as String? ?? 'normal';
    SpeechSpeed parsedSpeed;
    switch (speedStr.toLowerCase()) {
      case 'slow':
        parsedSpeed = SpeechSpeed.slow;
        break;
      case 'fast':
        parsedSpeed = SpeechSpeed.fast;
        break;
      case 'normal':
      default:
        parsedSpeed = SpeechSpeed.normal;
    }

    return AppSettings(
      voiceGuidanceEnabled: json['voice_guidance_enabled'] as bool? ?? true,
      hapticsEnabled: json['haptics_enabled'] as bool? ?? true,
      speechSpeed: parsedSpeed,
      languageCode: json['language_code'] as String? ?? 'en-US',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'voice_guidance_enabled': voiceGuidanceEnabled,
      'haptics_enabled': hapticsEnabled,
      'speech_speed': speechSpeed.name,
      'language_code': languageCode,
    };
  }
}
