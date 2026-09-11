class ApiConfig {
  static String? _customBaseUrl;

  /// Returns the configured base URL for the backend verification service.
  /// Defaults to standard Android emulator loopback (http://10.0.2.2:8000).
  /// Can be overridden at build-time via `--dart-define=API_BASE_URL=http://<IP>:8000`
  /// or at runtime via [customBaseUrl].
  static String get baseUrl {
    if (_customBaseUrl != null && _customBaseUrl!.isNotEmpty) {
      return _customBaseUrl!;
    }
    const envUrl = String.fromEnvironment('API_BASE_URL');
    if (envUrl.isNotEmpty) {
      return envUrl;
    }
    return 'http://10.0.2.2:8000';
  }

  static set customBaseUrl(String? url) {
    _customBaseUrl = url;
  }

  /// Returns the configured base URL for the assistant service.
  static String get assistantUrl {
    const envUrl = String.fromEnvironment('ASSISTANT_BASE_URL');
    if (envUrl.isNotEmpty) {
      return envUrl;
    }
    return 'http://10.0.2.2:3000';
  }
}
