import 'package:flutter/material.dart';
import '../../../core/accessibility/accessibility_theme.dart';
import '../../../core/accessibility/talkback_helpers.dart';
import '../../../services/tts/tts_service.dart';
import '../../../services/stt/stt_service.dart';
import '../../../services/api/api_service.dart';
import '../../../shared/models/verification_model.dart';
import '../../../shared/widgets/accessible_buttons.dart';
import '../../../shared/widgets/accessible_cards.dart';
import '../../../shared/widgets/accessible_states.dart';
import '../gestures/accessible_gesture_controller.dart';
import '../navigation/accessibility_router.dart';
import 'assistant_controller.dart';

class AccessibleAssistantScreen extends StatefulWidget {
  final TTSService ttsService;
  final ApiService apiService;
  final VerificationResult? verificationResult;

  const AccessibleAssistantScreen({
    super.key,
    required this.ttsService,
    required this.apiService,
    this.verificationResult,
  });

  @override
  State<AccessibleAssistantScreen> createState() => _AccessibleAssistantScreenState();
}

class _AccessibleAssistantScreenState extends State<AccessibleAssistantScreen> {
  late AssistantController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AssistantController(
      ttsService: widget.ttsService,
      sttService: STTService(),
      result: widget.verificationResult,
    );

    WidgetsBinding.instance.addPostFrameCallback((_) {
      _controller.speakInitialGreeting();
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<AssistantState>(
      valueListenable: _controller,
      builder: (context, state, _) {
        return AccessibleGestureController(
          ttsService: widget.ttsService,
          onDoubleTapScan: _controller.startListening,
          onSwipeUpHome: () => Navigator.popUntil(context, (route) => route.isFirst),
          onSwipeDownRepeat: _controller.repeatResponse,
          onTwoFingerTapHelp: () => AccessibilityRouter.navigateToHelp(context, widget.ttsService),
          child: Scaffold(
            backgroundColor: AccessibilityTheme.background,
            appBar: AppBar(
              title: const Text('Voice Assistant'),
              backgroundColor: AccessibilityTheme.background,
              leading: IconButton(
                icon: const Icon(Icons.arrow_back, size: 28, color: AccessibilityTheme.accessibilityHighlight),
                onPressed: () => Navigator.pop(context),
              ),
            ),
            body: SafeArea(
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // 1. Verified Medicine Context Banner
                    if (state.verificationResult != null && state.verificationResult!.medicine != null) ...[
                      TalkBackSemantics(
                        label: 'Active Verified Medicine Context: ${state.verificationResult!.medicine!.name}. Dosage: ${state.verificationResult!.medicine!.dosage}.',
                        isHeader: true,
                        child: Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: AccessibilityTheme.surface,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: AccessibilityTheme.primary),
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.medication, color: AccessibilityTheme.primary, size: 36),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      state.verificationResult!.medicine!.name.toUpperCase(),
                                      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.extrabold, color: AccessibilityTheme.accessibilityHighlight),
                                    ),
                                    const SizedBox(height: 2),
                                    Text(
                                      'Strength: ${state.verificationResult!.medicine!.dosage}',
                                      style: const TextStyle(fontSize: 15, color: AccessibilityTheme.textSecondary),
                                    ),
                                  ],
                                ),
                              ),
                              VerificationStatusBadge(
                                statusText: state.verificationResult!.status.name.toUpperCase(),
                                backgroundColor: AccessibilityTheme.success,
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                    ] else ...[
                      // Missing Context Alert
                      StatusCard(
                        title: 'No Active Medicine Scan',
                        message: 'Ask general medicine questions or scan a medicine code first for specific details.',
                        icon: Icons.info_outline,
                        color: AccessibilityTheme.primary,
                      ),
                      const SizedBox(height: 16),
                    ],

                    // 2. User Query Box
                    TalkBackSemantics(
                      label: 'Your Question: ${state.userQuery}',
                      child: Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: AccessibilityTheme.surface,
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(color: AccessibilityTheme.primary.withOpacity(0.5)),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('YOU SAID:', style: TextStyle(fontSize: 14, color: AccessibilityTheme.primary, fontWeight: FontWeight.bold)),
                            const SizedBox(height: 6),
                            Text(
                              state.userQuery,
                              style: const TextStyle(fontSize: 18, color: AccessibilityTheme.textPrimary, fontWeight: FontWeight.w600),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // 3. Assistant Response Box
                    Expanded(
                      child: TalkBackSemantics(
                        label: 'Assistant Response: ${state.assistantResponse}',
                        child: Container(
                          padding: const EdgeInsets.all(18),
                          decoration: BoxDecoration(
                            color: AccessibilityTheme.surface,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: AccessibilityTheme.accessibilityHighlight, width: 2),
                          ),
                          child: SingleChildScrollView(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text('ASSISTANT RESPONSE:', style: TextStyle(fontSize: 14, color: AccessibilityTheme.accessibilityHighlight, fontWeight: FontWeight.bold)),
                                const SizedBox(height: 10),
                                if (state.isProcessing)
                                  const AccessibleLoadingState(message: 'Processing voice query...')
                                else
                                  Text(
                                    state.assistantResponse,
                                    style: const TextStyle(fontSize: 20, color: AccessibilityTheme.textPrimary, fontWeight: FontWeight.bold, height: 1.4),
                                  ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // 4. Voice Action Microphone Button
                    VoiceActionButton(
                      label: state.isListening ? 'STOP LISTENING' : 'SPEAK YOUR QUESTION',
                      isListening: state.isListening,
                      onPressed: _controller.startListening,
                    ),
                    const SizedBox(height: 12),

                    // 5. Repeat Response Button
                    AccessibleSecondaryButton(
                      label: 'REPEAT RESPONSE',
                      icon: Icons.replay,
                      onPressed: _controller.repeatResponse,
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}
