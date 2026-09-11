import 'package:flutter/material.dart';
import '../../../core/accessibility/talkback_helpers.dart';
import '../../../services/tts/tts_service.dart';
import '../../../services/api/api_service.dart';
import '../gestures/accessible_gesture_controller.dart';
import '../scanner/accessible_scanner_screen.dart';
import '../assistant/accessible_assistant_screen.dart';
import '../history/accessible_history_screen.dart';
import '../settings/accessible_settings_screen.dart';

class AccessibleHomeScreen extends StatefulWidget {
  final TTSService ttsService;
  final ApiService apiService;

  const AccessibleHomeScreen({
    super.key,
    required this.ttsService,
    required this.apiService,
  });

  @override
  State<AccessibleHomeScreen> createState() => _AccessibleHomeScreenState();
}

class _AccessibleHomeScreenState extends State<AccessibleHomeScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      widget.ttsService.speak(
        "Accessible Medicine App Home. Double tap anywhere to start scanning. Long press for Voice Assistant. Two finger tap for help.",
      );
    });
  }

  void _navigateToScanner() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => AccessibleScannerScreen(
          ttsService: widget.ttsService,
          apiService: widget.apiService,
        ),
      ),
    );
  }

  void _navigateToAssistant() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => AccessibleAssistantScreen(
          ttsService: widget.ttsService,
          apiService: widget.apiService,
        ),
      ),
    );
  }

  void _navigateToHistory() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => AccessibleHistoryScreen(
          ttsService: widget.ttsService,
          apiService: widget.apiService,
        ),
      ),
    );
  }

  void _navigateToSettings() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => AccessibleSettingsScreen(
          ttsService: widget.ttsService,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AccessibleGestureController(
      ttsService: widget.ttsService,
      onDoubleTapScan: _navigateToScanner,
      onLongPressAssistant: _navigateToAssistant,
      onSwipeRightNext: _navigateToHistory,
      onSwipeDownRepeat: () {
        widget.ttsService.speak(
          "Accessible Medicine Home. Double tap to scan. Long press for assistant. Swipe right for history. Swipe left for settings.",
        );
      },
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Accessible Medicine Assistant'),
          backgroundColor: Colors.black,
        ),
        body: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TalkBackSemantics(
                label: "Scan Medicine Code Button. Large yellow button. Double tap to open camera scanner.",
                hint: "Triggers DataMatrix and QR code scanner",
                isHeader: true,
                onTap: _navigateToScanner,
                child: Container(
                  height: 140,
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFD700),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: const [
                        Icon(Icons.qr_code_scanner, size: 56, color: Colors.black),
                        SizedBox(height: 8),
                        Text(
                          'SCAN MEDICINE CODE',
                          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.black),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Expanded(
                child: Row(
                  children: [
                    Expanded(
                      child: TalkBackSemantics(
                        label: "Voice Assistant Button. Cyan button. Long press or tap to speak query.",
                        onTap: _navigateToAssistant,
                        child: Container(
                          decoration: BoxDecoration(
                            color: const Color(0xFF00FFFF),
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: const [
                                Icon(Icons.mic, size: 48, color: Colors.black),
                                SizedBox(height: 8),
                                Text('VOICE\nASSISTANT', textAlign: TextAlign.center, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.black)),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: TalkBackSemantics(
                        label: "Scan History Button. Green button. Tap to hear previous scans.",
                        onTap: _navigateToHistory,
                        child: Container(
                          decoration: BoxDecoration(
                            color: const Color(0xFF33FF99),
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: const [
                                Icon(Icons.history, size: 48, color: Colors.black),
                                SizedBox(height: 8),
                                Text('SCAN\nHISTORY', textAlign: TextAlign.center, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.black)),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              TalkBackSemantics(
                label: "Settings Button. Large grey button. Tap for accessibility settings.",
                onTap: _navigateToSettings,
                child: Container(
                  height: 72,
                  decoration: BoxDecoration(
                    color: const Color(0xFF333333),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.white, width: 2),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: const [
                      Icon(Icons.settings, size: 32, color: Colors.white),
                      SizedBox(width: 12),
                      Text('ACCESSIBILITY SETTINGS', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
