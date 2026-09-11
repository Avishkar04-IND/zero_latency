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
    bool parseBool(dynamic val, bool defaultValue) {
      if (val is bool) return val;
      if (val is String) {
        if (val.toLowerCase() == 'true') return true;
        if (val.toLowerCase() == 'false') return false;
      }
      return defaultValue;
    }

    final speedRaw = json['speech_speed'];
    final speedStr = speedRaw is String ? speedRaw.toLowerCase() : 'normal';
    SpeechSpeed parsedSpeed;
    switch (speedStr) {
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

    final langRaw = json['language_code'];
    final langStr = langRaw is String && langRaw.isNotEmpty ? langRaw : 'en-US';

    return AppSettings(
      voiceGuidanceEnabled: parseBool(json['voice_guidance_enabled'], true),
      hapticsEnabled: parseBool(json['haptics_enabled'], true),
      speechSpeed: parsedSpeed,
      languageCode: langStr,
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

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is AppSettings &&
        other.voiceGuidanceEnabled == voiceGuidanceEnabled &&
        other.hapticsEnabled == hapticsEnabled &&
        other.speechSpeed == speechSpeed &&
        other.languageCode == languageCode;
  }

  @override
  int get hashCode {
    return Object.hash(
      voiceGuidanceEnabled,
      hapticsEnabled,
      speechSpeed,
      languageCode,
    );
  }
}
