import 'package:flutter/material.dart';
import '../../../core/accessibility/accessibility_theme.dart';
import '../../../services/tts/tts_service.dart';
import '../gestures/accessible_gesture_controller.dart';

class AccessibleHelpScreen extends StatefulWidget {
  final TTSService ttsService;

  const AccessibleHelpScreen({
    super.key,
    required this.ttsService,
  });

  @override
  State<AccessibleHelpScreen> createState() => _AccessibleHelpScreenState();
}

class _AccessibleHelpScreenState extends State<AccessibleHelpScreen> {
  final String _helpOverview =
      "Zero Latency Help & Gesture Guide. Double tap anywhere on screen to start medicine scan. Swipe right for next option. Swipe left for previous. Swipe down to repeat audio prompt. Swipe up to return home. Long press to activate Voice Assistant. Two finger tap to open this help menu.";

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      widget.ttsService.speak(_helpOverview);
    });
  }

  @override
  Widget build(BuildContext context) {
    return AccessibleGestureController(
      ttsService: widget.ttsService,
      onSwipeUpHome: () => Navigator.pop(context),
      onSwipeDownRepeat: () => widget.ttsService.speak(_helpOverview),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Help & Gesture Guide'),
          backgroundColor: Colors.black,
        ),
        body: Container(
          color: AccessibilityTheme.background,
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Expanded(
                child: ListView(
                  children: [
                    _buildGestureTile("Double Tap", "Start Medicine Scanner", Icons.touch_app),
                    _buildGestureTile("Long Press", "Activate Voice Assistant", Icons.mic),
                    _buildGestureTile("Swipe Right", "Navigate to Next Item", Icons.arrow_forward),
                    _buildGestureTile("Swipe Left", "Navigate to Previous Item", Icons.arrow_back),
                    _buildGestureTile("Swipe Down", "Repeat Audio Voice Prompt", Icons.replay),
                    _buildGestureTile("Swipe Up", "Return to Home Screen", Icons.home),
                    _buildGestureTile("Two Finger Tap", "Open Help & Gesture Guide", Icons.help_outline),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AccessibilityTheme.accessibilityHighlight,
                  foregroundColor: AccessibilityTheme.textDark,
                  minimumSize: const Size(double.infinity, 64),
                ),
                onPressed: () => widget.ttsService.speak(_helpOverview),
                icon: const Icon(Icons.volume_up, size: 28),
                label: const Text('READ HELP ALOUD'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildGestureTile(String gesture, String action, IconData icon) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AccessibilityTheme.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AccessibilityTheme.primary.withOpacity(0.5)),
      ),
      child: Row(
        children: [
          Icon(icon, size: 32, color: AccessibilityTheme.accessibilityHighlight),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(gesture, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AccessibilityTheme.primary)),
                const SizedBox(height: 4),
                Text(action, style: const TextStyle(fontSize: 16, color: AccessibilityTheme.textPrimary)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
