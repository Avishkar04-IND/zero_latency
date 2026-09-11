import 'package:flutter/material.dart';
import '../../../core/accessibility/accessibility_theme.dart';
import '../../../core/accessibility/talkback_helpers.dart';
import '../../../services/tts/tts_service.dart';
import '../../../shared/models/verification_model.dart';
import '../../../shared/widgets/accessible_buttons.dart';
import '../gestures/accessible_gesture_controller.dart';
import '../navigation/accessibility_router.dart';
import 'medicine_reader_controller.dart';
import 'medicine_information_section.dart';

class AccessibleMedicineReaderScreen extends StatefulWidget {
  final VerificationResult verificationResult;
  final TTSService ttsService;

  const AccessibleMedicineReaderScreen({
    super.key,
    required this.verificationResult,
    required this.ttsService,
  });

  @override
  State<AccessibleMedicineReaderScreen> createState() => _AccessibleMedicineReaderScreenState();
}

class _AccessibleMedicineReaderScreenState extends State<AccessibleMedicineReaderScreen> {
  late MedicineReaderController _controller;
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _controller = MedicineReaderController(
      result: widget.verificationResult,
      ttsService: widget.ttsService,
    );
    _controller.addListener(_onControllerStateChanged);

    WidgetsBinding.instance.addPostFrameCallback((_) {
      _controller.speakCurrentSection();
    });
  }

  void _onControllerStateChanged() {
    if (mounted) {
      setState(() {});
    }
  }

  @override
  void dispose() {
    _controller.removeListener(_onControllerStateChanged);
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = _controller.state;
    final sections = state.sections;

    return AccessibleGestureController(
      ttsService: widget.ttsService,
      onSwipeRightNext: _controller.nextSection,
      onSwipeLeftPrevious: _controller.previousSection,
      onSwipeDownRepeat: _controller.speakCurrentSection,
      onSwipeUpHome: () => Navigator.popUntil(context, (route) => route.isFirst),
      onTwoFingerTapHelp: () => AccessibilityRouter.navigateToHelp(context, widget.ttsService),
      child: Scaffold(
        backgroundColor: AccessibilityTheme.background,
        appBar: AppBar(
          title: Text(
            'Medicine Reader (${state.currentIndex + 1}/${sections.length})',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          backgroundColor: AccessibilityTheme.background,
          actions: [
            IconButton(
              icon: const Icon(Icons.help_outline, color: AccessibilityTheme.primary, size: 28),
              onPressed: () => AccessibilityRouter.navigateToHelp(context, widget.ttsService),
            ),
          ],
        ),
        body: SafeArea(
          child: Column(
            children: [
              // Top Medical Safety & Reader Instructions Header
              TalkBackSemantics(
                label: 'Voice-first Medicine Reader active. Section ${state.currentIndex + 1} of ${sections.length}. Swipe right for next info section, swipe left for previous, swipe down to repeat audio.',
                isHeader: true,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  color: AccessibilityTheme.surface,
                  child: Row(
                    children: [
                      const Icon(Icons.volume_up, color: AccessibilityTheme.accessibilityHighlight, size: 24),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          'Swipe right for NEXT • Swipe left for PREVIOUS',
                          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AccessibilityTheme.textSecondary),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              // Structured Sections Scrollable List
              Expanded(
                child: ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(16),
                  itemCount: sections.length + 1,
                  itemBuilder: (context, index) {
                    if (index == sections.length) {
                      // Medical Safety & Source Disclaimer Footer
                      return Container(
                        margin: const EdgeInsets.only(top: 16, bottom: 24),
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: AccessibilityTheme.surface.withOpacity(0.6),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.white12),
                        ),
                        child: Row(
                          children: const [
                            Icon(Icons.shield_outlined, color: AccessibilityTheme.textSecondary, size: 28),
                            SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                'Source: Verified manufacturer database. App does not provide medical diagnosis.',
                                style: TextStyle(fontSize: 13, color: AccessibilityTheme.textSecondary),
                              ),
                            ),
                          ],
                        ),
                      );
                    }

                    final sec = sections[index];
                    final isActive = index == state.currentIndex;

                    return MedicineInformationSectionWidget(
                      section: sec,
                      isActive: isActive,
                      onTap: () => _controller.jumpToSection(index),
                    );
                  },
                ),
              ),

              // Bottom Reader Navigation Controls Bar
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                color: AccessibilityTheme.surface,
                child: Row(
                  children: [
                    Expanded(
                      child: AccessibleIconButton(
                        icon: Icons.arrow_back,
                        label: 'Previous Information Section',
                        hint: 'Reads previous section aloud',
                        onPressed: _controller.previousSection,
                        color: state.currentIndex > 0 ? AccessibilityTheme.primary : Colors.grey,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      flex: 2,
                      child: AccessiblePrimaryButton(
                        label: 'REPEAT AUDIO',
                        semanticHint: 'Repeats audio speech for current section',
                        icon: Icons.replay,
                        height: 56,
                        backgroundColor: AccessibilityTheme.accessibilityHighlight,
                        onPressed: _controller.speakCurrentSection,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: AccessibleIconButton(
                        icon: Icons.arrow_forward,
                        label: 'Next Information Section',
                        hint: 'Reads next section aloud',
                        onPressed: _controller.nextSection,
                        color: state.currentIndex < sections.length - 1 ? AccessibilityTheme.primary : Colors.grey,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
