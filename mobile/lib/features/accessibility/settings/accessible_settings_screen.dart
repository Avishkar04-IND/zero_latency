import 'package:flutter/material.dart';
import '../../../core/accessibility/accessibility_theme.dart';
import '../../../core/accessibility/talkback_helpers.dart';
import '../../../services/tts/tts_service.dart';
import '../../../services/haptics/haptics_service.dart';
import '../../../services/api/api_service.dart';
import '../../../services/settings/settings_service.dart';
import '../../../services/settings/local_settings_service.dart';
import '../../../shared/models/app_settings.dart';
import '../../../shared/widgets/accessible_buttons.dart';
import '../../../shared/widgets/accessible_cards.dart';
import '../../../shared/widgets/accessible_states.dart';
import '../gestures/accessible_gesture_controller.dart';
import '../navigation/accessibility_router.dart';
import 'settings_controller.dart';

class AccessibleSettingsScreen extends StatefulWidget {
  final TTSService ttsService;
  final ApiService? apiService;
  final SettingsService? settingsService;

  const AccessibleSettingsScreen({
    super.key,
    required this.ttsService,
    this.apiService,
    this.settingsService,
  });

  @override
  State<AccessibleSettingsScreen> createState() => _AccessibleSettingsScreenState();
}

class _AccessibleSettingsScreenState extends State<AccessibleSettingsScreen> {
  late SettingsController _controller;
  late SettingsService _settingsService;

  @override
  void initState() {
    super.initState();
    _settingsService = widget.settingsService ?? LocalSettingsService(ttsService: widget.ttsService);
    _controller = SettingsController(
      settingsService: _settingsService,
      ttsService: widget.ttsService,
    );

    _controller.loadSettings(speakInitial: true);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _showAccessibilityInfoDialog(BuildContext context) {
    HapticsService.scanningTick();
    widget.ttsService.speak("Accessibility Information. Zero Latency features high contrast dark theme, screen reader semantic headers, tactile vibration feedback, and screen-free voice scanner guidance.");

    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        backgroundColor: const Color(0xFF151B22),
        shape: RoundedRectangleBorder(
          side: const BorderSide(color: AccessibilityTheme.primary, width: 3),
          borderRadius: BorderRadius.circular(16),
        ),
        title: TalkBackSemantics(
          label: 'Accessibility Support Overview',
          isHeader: true,
          child: Row(
            children: const [
              Icon(Icons.accessibility_new, color: AccessibilityTheme.accessibilityHighlight, size: 32),
              SizedBox(width: 12),
              Text(
                'ACCESSIBILITY SUPPORT',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AccessibilityTheme.accessibilityHighlight),
              ),
            ],
          ),
        ),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: const [
              Text(
                '• TalkBack & Screen Reader Compatible: Full semantic titles, labels, and focus ordering.\n'
                '• High-Contrast Design System: High-contrast text on deep dark surface backgrounds.\n'
                '• Voice-Guided Positioning: Non-visual camera feedback guiding distance and code alignment.\n'
                '• Tactile Vibrations: Custom haptic patterns for authentic, expired, and suspicious alerts.\n'
                '• Touch & Swipe Shortcuts: Intuitive screen-wide gestures without precise target requirements.',
                style: TextStyle(fontSize: 16, color: AccessibilityTheme.textPrimary, height: 1.5),
              ),
            ],
          ),
        ),
        actions: [
          AccessiblePrimaryButton(
            label: 'CLOSE',
            icon: Icons.check,
            onPressed: () => Navigator.pop(dialogContext),
          ),
        ],
      ),
    );
  }

  void _showAboutDialog(BuildContext context) {
    HapticsService.scanningTick();
    widget.ttsService.speak("About Zero Latency. Accessibility-first medicine verification system for visually impaired and elderly users.");

    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        backgroundColor: const Color(0xFF151B22),
        shape: RoundedRectangleBorder(
          side: const BorderSide(color: AccessibilityTheme.accessibilityHighlight, width: 3),
          borderRadius: BorderRadius.circular(16),
        ),
        title: TalkBackSemantics(
          label: 'About Zero Latency',
          isHeader: true,
          child: Row(
            children: const [
              Icon(Icons.shield_outlined, color: AccessibilityTheme.accessibilityHighlight, size: 32),
              SizedBox(width: 12),
              Text(
                'ZERO LATENCY',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.extrabold, color: AccessibilityTheme.accessibilityHighlight),
              ),
            ],
          ),
        ),
        content: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: const [
            Text(
              'Accessibility-first medicine verification platform.',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
            ),
            SizedBox(height: 12),
            Text(
              'Empowering visually impaired, blind, and elderly individuals to independently verify prescription medicines, read dosage instructions, and check expiration dates using voice guidance and screen readers.',
              style: TextStyle(fontSize: 16, color: AccessibilityTheme.textSecondary, height: 1.4),
            ),
          ],
        ),
        actions: [
          AccessiblePrimaryButton(
            label: 'CLOSE',
            icon: Icons.check,
            onPressed: () => Navigator.pop(dialogContext),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<SettingsState>(
      valueListenable: _controller,
      builder: (context, state, _) {
        final settings = state.settings;

        return AccessibleGestureController(
          ttsService: widget.ttsService,
          onSwipeUpHome: () => Navigator.pop(context),
          onSwipeDownRepeat: () => widget.ttsService.speak(
            "Settings menu. Voice guidance is ${settings.voiceGuidanceEnabled ? 'ON' : 'OFF'}. Haptics is ${settings.hapticsEnabled ? 'ON' : 'OFF'}. Speech speed is ${settings.speechSpeedLabel}.",
          ),
          onTwoFingerTapHelp: () => AccessibilityRouter.navigateToHelp(context, widget.ttsService),
          child: Scaffold(
            backgroundColor: AccessibilityTheme.background,
            appBar: AppBar(
              backgroundColor: AccessibilityTheme.background,
              elevation: 0,
              leading: IconButton(
                icon: const Icon(Icons.arrow_back, size: 28, color: AccessibilityTheme.accessibilityHighlight),
                onPressed: () => Navigator.pop(context),
                tooltip: 'Back to Home',
              ),
              title: TalkBackSemantics(
                label: 'Accessibility Settings and Preferences Screen',
                isHeader: true,
                child: const Text(
                  'SETTINGS',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.extrabold,
                    color: AccessibilityTheme.accessibilityHighlight,
                    letterSpacing: 1.0,
                  ),
                ),
              ),
            ),
            body: SafeArea(
              child: state.isLoading
                  ? const AccessibleLoadingState(message: 'Loading preferences...')
                  : SingleChildScrollView(
                      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          // 1. Voice Guidance Switch Card
                          _buildToggleSettingCard(
                            title: 'VOICE GUIDANCE',
                            subtitle: settings.voiceGuidanceEnabled
                                ? 'Spoken prompts and guidance active'
                                : 'Voice audio prompts disabled',
                            isEnabled: settings.voiceGuidanceEnabled,
                            icon: Icons.record_voice_over,
                            onChanged: (val) => _controller.toggleVoiceGuidance(val),
                          ),
                          const SizedBox(height: 16),

                          // 2. Haptics Switch Card
                          _buildToggleSettingCard(
                            title: 'TACTILE HAPTIC VIBRATIONS',
                            subtitle: settings.hapticsEnabled
                                ? 'Vibration patterns enabled for scan alerts'
                                : 'Vibrations turned off',
                            isEnabled: settings.hapticsEnabled,
                            icon: Icons.vibration,
                            onChanged: (val) => _controller.toggleHaptics(val),
                          ),
                          const SizedBox(height: 20),

                          // 3. Speech Rate Speed Selector
                          _buildSpeechSpeedSection(settings.speechSpeed),
                          const SizedBox(height: 20),

                          // 4. Language Architecture Card
                          _buildLanguageCard(settings.languageDisplay),
                          const SizedBox(height: 20),

                          // 5. Section Heading: HELP & ABOUT
                          const Text(
                            'GUIDES & ABOUT',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: AccessibilityTheme.primary,
                              letterSpacing: 1.0,
                            ),
                          ),
                          const SizedBox(height: 12),

                          // 6. Gesture Help Card
                          AccessibleCard(
                            label: 'Gesture Help Card. Double tap to review non-visual touch and swipe shortcuts.',
                            title: 'Gesture Help & Shortcuts',
                            subtitle: 'View touch, double tap, and swipe gesture controls',
                            icon: Icons.help_outline,
                            accentColor: AccessibilityTheme.primary,
                            onTap: () => AccessibilityRouter.navigateToHelp(context, widget.ttsService),
                          ),
                          const SizedBox(height: 12),

                          // 7. Accessibility Info Card
                          AccessibleCard(
                            label: 'Accessibility Information Card. Double tap to view screen reader and TalkBack details.',
                            title: 'Accessibility Information',
                            subtitle: 'TalkBack compatibility & high-contrast design info',
                            icon: Icons.accessibility_new,
                            accentColor: AccessibilityTheme.success,
                            onTap: () => _showAccessibilityInfoDialog(context),
                          ),
                          const SizedBox(height: 12),

                          // 8. About Card
                          AccessibleCard(
                            label: 'About Zero Latency Card. Double tap to view application overview.',
                            title: 'About Zero Latency',
                            subtitle: 'Accessibility-first medicine verification overview',
                            icon: Icons.info_outline,
                            accentColor: AccessibilityTheme.accessibilityHighlight,
                            onTap: () => _showAboutDialog(context),
                          ),
                          const SizedBox(height: 24),
                        ],
                      ),
                    ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildToggleSettingCard({
    required String title,
    required String subtitle,
    required bool isEnabled,
    required IconData icon,
    required ValueChanged<bool> onChanged,
  }) {
    final statusColor = isEnabled ? AccessibilityTheme.success : AccessibilityTheme.textSecondary;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF151B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: statusColor, width: 2),
      ),
      child: Semantics(
        label: '$title. Currently ${isEnabled ? 'ON' : 'OFF'}. $subtitle.',
        hint: 'Double tap to toggle setting',
        child: Row(
          children: [
            Icon(icon, size: 36, color: statusColor),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          title,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: statusColor.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(color: statusColor, width: 1),
                        ),
                        child: Text(
                          isEnabled ? 'ON' : 'OFF',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.extrabold,
                            color: statusColor,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: const TextStyle(
                      fontSize: 15,
                      color: AccessibilityTheme.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            Switch(
              value: isEnabled,
              activeColor: AccessibilityTheme.success,
              activeTrackColor: AccessibilityTheme.success.withOpacity(0.3),
              inactiveThumbColor: AccessibilityTheme.textSecondary,
              inactiveTrackColor: Colors.black,
              onChanged: onChanged,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSpeechSpeedSection(SpeechSpeed currentSpeed) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF151B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AccessibilityTheme.primary, width: 2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          TalkBackSemantics(
            label: 'Speech Speed Setting. Currently set to ${currentSpeed.name}.',
            isHeader: true,
            child: Row(
              children: const [
                Icon(Icons.speed, color: AccessibilityTheme.primary, size: 28),
                SizedBox(width: 10),
                Text(
                  'SPEECH READOUT SPEED',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: AccessibilityTheme.primary,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              Expanded(child: _buildSpeedButton('SLOW', SpeechSpeed.slow, currentSpeed)),
              const SizedBox(width: 8),
              Expanded(child: _buildSpeedButton('NORMAL', SpeechSpeed.normal, currentSpeed)),
              const SizedBox(width: 8),
              Expanded(child: _buildSpeedButton('FAST', SpeechSpeed.fast, currentSpeed)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSpeedButton(String label, SpeechSpeed speed, SpeechSpeed selectedSpeed) {
    final isSelected = speed == selectedSpeed;
    final bgColor = isSelected ? AccessibilityTheme.accessibilityHighlight : const Color(0xFF222B35);
    final fgColor = isSelected ? Colors.black : Colors.white;

    return Semantics(
      label: '$label speech speed. ${isSelected ? 'Currently selected.' : 'Double tap to select.'}',
      button: true,
      selected: isSelected,
      child: InkWell(
        onTap: () => _controller.setSpeechSpeed(speed),
        borderRadius: BorderRadius.circular(10),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 14),
          decoration: BoxDecoration(
            color: bgColor,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: isSelected ? AccessibilityTheme.accessibilityHighlight : AccessibilityTheme.textSecondary,
              width: 2,
            ),
          ),
          alignment: Alignment.center,
          child: Text(
            label,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: fgColor,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLanguageCard(String currentLanguage) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF151B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AccessibilityTheme.warning, width: 2),
      ),
      child: Semantics(
        label: 'App Language Setting. Currently $currentLanguage.',
        child: Row(
          children: [
            const Icon(Icons.language, color: AccessibilityTheme.warning, size: 32),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'APP LANGUAGE',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: AccessibilityTheme.warning,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    currentLanguage,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 2),
                  const Text(
                    'Primary supported voice language',
                    style: TextStyle(
                      fontSize: 14,
                      color: AccessibilityTheme.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
