import 'package:flutter/material.dart';
import '../core/accessibility/accessibility_theme.dart';
import '../services/api/api_service.dart';
import '../services/api/mock_api_service.dart';
import '../services/tts/tts_service.dart';
import '../services/history/history_service.dart';
import '../services/history/local_history_service.dart';
import '../features/accessibility/home/accessible_home_screen.dart';
import '../features/normal_user/normal_user_home_screen.dart';

class ExperienceSelectorApp extends StatefulWidget {
  const ExperienceSelectorApp({super.key});

  @override
  State<ExperienceSelectorApp> createState() => _ExperienceSelectorAppState();
}

class _ExperienceSelectorAppState extends State<ExperienceSelectorApp> {
  final ApiService _apiService = MockApiService();
  final TTSService _ttsService = TTSService();
  final HistoryService _historyService = LocalHistoryService();
  bool _isAccessibilityMode = true; // Default to accessible experience for Member 4

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
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              _isAccessibilityMode ? "MODE: ACCESSIBLE (VISUALLY IMPAIRED)" : "MODE: STANDARD USER",
              style: TextStyle(
                fontSize: 14,
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
      ),
    );
  }
}
