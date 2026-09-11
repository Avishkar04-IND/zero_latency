import 'package:flutter/material.dart';
import '../../../core/accessibility/accessibility_theme.dart';
import '../../../core/accessibility/talkback_helpers.dart';
import '../../../services/tts/tts_service.dart';
import '../../../services/haptics/haptics_service.dart';
import '../../../services/api/api_service.dart';
import '../../../shared/widgets/accessible_buttons.dart';
import '../../../shared/widgets/accessible_cards.dart';
import '../../../shared/widgets/accessible_states.dart';
import '../gestures/accessible_gesture_controller.dart';
import '../navigation/accessibility_router.dart';

enum AccessibilityHomeState {
  normal,
  loading,
  voiceDisabled,
  offline,
  error,
}

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
  AccessibilityHomeState _currentState = AccessibilityHomeState.normal;
  bool _isVoiceMuted = false;
  String _errorMessage = '';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _speakWelcome();
    });
  }

  void _speakWelcome() {
    if (!_isVoiceMuted) {
      widget.ttsService.speak(
        "Welcome to Zero Latency. Double tap Scan Medicine to begin.",
      );
    }
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  }

  void _onScanPressed() {
    HapticsService.verifiedAuthentic();
    AccessibilityRouter.navigateToScanner(context, widget.ttsService, widget.apiService);
  }

  void _onAssistantPressed() {
    HapticsService.codeDetected();
    AccessibilityRouter.navigateToAssistant(context, widget.ttsService, widget.apiService);
  }

  void _onHistoryPressed() {
    HapticsService.scanningTick();
    AccessibilityRouter.navigateToHistory(context, widget.ttsService, widget.apiService);
  }

  void _onSettingsPressed() {
    HapticsService.scanningTick();
    AccessibilityRouter.navigateToSettings(context, widget.ttsService);
  }

  void _onHelpPressed() {
    HapticsService.scanningTick();
    AccessibilityRouter.navigateToHelp(context, widget.ttsService);
  }

  @override
  Widget build(BuildContext context) {
    return AccessibleGestureController(
      ttsService: widget.ttsService,
      onDoubleTapScan: _onScanPressed,
      onLongPressAssistant: _onAssistantPressed,
      onSwipeRightNext: _onHistoryPressed,
      onSwipeLeftPrevious: _onSettingsPressed,
      onSwipeDownRepeat: _speakWelcome,
      onTwoFingerTapHelp: _onHelpPressed,
      child: Scaffold(
        backgroundColor: AccessibilityTheme.background,
        appBar: AppBar(
          backgroundColor: AccessibilityTheme.background,
          elevation: 0,
          title: TalkBackSemantics(
            label: 'Zero Latency Accessible Medicine App Home',
            isHeader: true,
            child: Row(
              children: const [
                Icon(Icons.shield_outlined, color: AccessibilityTheme.primary, size: 28),
                SizedBox(width: 10),
                Text(
                  'ZERO LATENCY',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.extrabold,
                    color: AccessibilityTheme.accessibilityHighlight,
                    letterSpacing: 1.0,
                  ),
                ),
              ],
            ),
          ),
        ),
        body: SafeArea(
          child: _buildBodyStateContent(),
        ),
      ),
    );
  }

  Widget _buildBodyStateContent() {
    switch (_currentState) {
      case AccessibilityHomeState.loading:
        return const AccessibleLoadingState(message: 'Initializing Zero Latency Accessibility Services...');
      case AccessibilityHomeState.error:
        return AccessibleErrorState(
          message: _errorMessage.isEmpty ? 'Failed to connect to core service.' : _errorMessage,
          onRetry: () {
            setState(() {
              _currentState = AccessibilityHomeState.normal;
            });
            _speakWelcome();
          },
        );
      case AccessibilityHomeState.normal:
      case AccessibilityHomeState.voiceDisabled:
      case AccessibilityHomeState.offline:
      default:
        return SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 1. Time-aware Greeting
              TalkBackSemantics(
                label: '${_getGreeting()}. Welcome to Zero Latency Accessible Medicine Platform.',
                isHeader: true,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _getGreeting(),
                      style: const TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: AccessibilityTheme.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Screen-free & voice-guided verification',
                      style: TextStyle(
                        fontSize: 16,
                        color: AccessibilityTheme.textSecondary,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // 2. Voice Guidance Control Banner
              VoiceGuidanceBanner(
                isVoiceEnabled: !_isVoiceMuted,
                onRepeatPressed: _speakWelcome,
                onToggleVoice: () {
                  setState(() {
                    _isVoiceMuted = !_isVoiceMuted;
                  });
                  if (!_isVoiceMuted) {
                    widget.ttsService.speak("Voice guidance enabled.");
                  }
                },
              ),
              const SizedBox(height: 20),

              // 3. DOMINANT PRIMARY SCAN ACTION
              AccessiblePrimaryButton(
                label: 'SCAN MEDICINE',
                semanticHint: 'Double tap to open voice-guided camera scanner',
                icon: Icons.qr_code_scanner,
                height: 120,
                backgroundColor: AccessibilityTheme.accessibilityHighlight,
                foregroundColor: AccessibilityTheme.textDark,
                onPressed: _onScanPressed,
              ),
              const SizedBox(height: 20),

              // 4. Section Heading
              const Text(
                'QUICK ACTIONS',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: AccessibilityTheme.primary,
                  letterSpacing: 1.0,
                ),
              ),
              const SizedBox(height: 12),

              // 5. Action Cards
              AccessibleCard(
                label: 'Voice Assistant Card. Double tap to speak questions about dosage or storage.',
                title: 'Voice Assistant',
                subtitle: 'Ask about dosage, storage, or medicine warnings',
                icon: Icons.mic_external_on,
                accentColor: AccessibilityTheme.primary,
                onTap: _onAssistantPressed,
              ),
              const SizedBox(height: 12),

              AccessibleCard(
                label: 'Scan History Card. Double tap to review past medicine verifications.',
                title: 'Scan History',
                subtitle: 'Review previous authentic & expired scans',
                icon: Icons.history,
                accentColor: AccessibilityTheme.success,
                onTap: _onHistoryPressed,
              ),
              const SizedBox(height: 12),

              AccessibleCard(
                label: 'Accessibility Settings Card. Adjust voice speed and vibration feedback.',
                title: 'Accessibility Settings',
                subtitle: 'Configure speech rate and haptic vibrations',
                icon: Icons.settings_accessibility,
                accentColor: AccessibilityTheme.warning,
                onTap: _onSettingsPressed,
              ),
              const SizedBox(height: 12),

              AccessibleCard(
                label: 'Help and Gesture Guide Card. Double tap to view touch and swipe shortcuts.',
                title: 'Help & Gesture Guide',
                subtitle: 'View screen reader & non-visual gesture shortcuts',
                icon: Icons.help_outline,
                accentColor: AccessibilityTheme.textSecondary,
                onTap: _onHelpPressed,
              ),
              const SizedBox(height: 24),
            ],
          ),
        );
    }
  }
}
