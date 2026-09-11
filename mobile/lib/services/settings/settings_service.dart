import '../../shared/models/app_settings.dart';

abstract class SettingsService {
  Future<AppSettings> getSettings();
  Future<void> updateSettings(AppSettings settings);
  Future<void> resetSettings();
}
