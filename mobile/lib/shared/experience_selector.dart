import 'package:flutter/material.dart';
import '../core/accessibility/accessibility_theme.dart';
import '../core/config/api_config.dart';
import '../services/api/api_service.dart';
import '../services/api/mock_api_service.dart';
import '../services/api/real_api_service.dart';
import '../services/tts/tts_service.dart';
import '../services/history/history_service.dart';
import '../services/history/local_history_service.dart';
import '../services/settings/settings_service.dart';
import '../services/settings/local_settings_service.dart';
import '../features/accessibility/home/accessible_home_screen.dart';
import '../features/normal_user/normal_user_home_screen.dart';

class ExperienceSelectorApp extends StatefulWidget {
  const ExperienceSelectorApp({super.key});

  @override
  State<ExperienceSelectorApp> createState() => _ExperienceSelectorAppState();
}

class _ExperienceSelectorAppState extends State<ExperienceSelectorApp> {
  final ApiService _mockApiService = MockApiService();
  final ApiService _realApiService = RealApiService();
  bool _useRealApi = const bool.fromEnvironment('USE_REAL_API', defaultValue: false);

  late final TTSService _ttsService;
  late final HistoryService _historyService;
  late final SettingsService _settingsService;
  bool _isAccessibilityMode = true; // Default to accessible experience for Member 4

  ApiService get _apiService => _useRealApi ? _realApiService : _mockApiService;

  @override
  void initState() {
    super.initState();
    _ttsService = TTSService();
    _historyService = LocalHistoryService();
    _settingsService = LocalSettingsService(ttsService: _ttsService);
  }

  @override
  Widget build(BuildContext context) {
    if (_isAccessibilityMode) {
      return MaterialApp(
        title: 'Smart Medicine Accessible App',
        debugShowCheckedModeBanner: false,
        theme: AccessibilityTheme.highContrastDarkTheme,
        home: Scaffold(
          body: Column(
            children: [
              _buildTopBanner(),
              Expanded(
                child: AccessibleHomeScreen(
                  ttsService: _ttsService,
                  apiService: _apiService,
                  historyService: _historyService,
                  settingsService: _settingsService,
                ),
              ),
            ],
          ),
        ),
      );
    } else {
      return MaterialApp(
        title: 'Smart Medicine Standard App',
        debugShowCheckedModeBanner: false,
        theme: ThemeData.light(useMaterial3: true),
        home: Scaffold(
          body: Column(
            children: [
              _buildTopBanner(),
              const Expanded(child: NormalUserHomeScreen()),
            ],
          ),
        ),
      );
    }
  }

  Widget _buildTopBanner() {
    return SafeArea(
      bottom: false,
      child: Container(
        color: const Color(0xFF1E1E1E),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  _isAccessibilityMode ? "MODE: ACCESSIBLE" : "MODE: STANDARD USER",
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                    color: _isAccessibilityMode ? const Color(0xFFFFD700) : Colors.blue,
                  ),
                ),
                Switch(
                  value: _isAccessibilityMode,
                  activeColor: const Color(0xFFFFD700),
                  onChanged: (val) {
                    setState(() {
                      _isAccessibilityMode = val;
                    });
                    if (val) {
                      _ttsService.speak("Switched to Visually Impaired Accessible Experience.");
                    }
                  },
                ),
              ],
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  _useRealApi ? "API: REAL BACKEND (${ApiConfig.baseUrl})" : "API: MOCK BACKEND",
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    color: _useRealApi ? Colors.greenAccent : Colors.orangeAccent,
                  ),
                ),
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      _useRealApi ? "REAL" : "MOCK",
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        color: _useRealApi ? Colors.greenAccent : Colors.orangeAccent,
                      ),
                    ),
                    const SizedBox(width: 4),
                    Switch(
                      value: _useRealApi,
                      activeColor: Colors.greenAccent,
                      onChanged: (val) {
                        setState(() {
                          _useRealApi = val;
                        });
                        final modeMsg = val
                            ? "Switched to Real Backend API service at ${ApiConfig.baseUrl}"
                            : "Switched to Mock API service";
                        _ttsService.speak(modeMsg);
                      },
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

