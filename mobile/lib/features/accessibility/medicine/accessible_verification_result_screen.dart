import 'package:flutter/material.dart';
import '../../../core/accessibility/accessibility_theme.dart';
import '../../../core/accessibility/talkback_helpers.dart';
import '../../../services/tts/tts_service.dart';
import '../../../services/haptics/haptics_service.dart';
import '../../../shared/models/verification_model.dart';
import '../../../shared/widgets/accessible_buttons.dart';
import '../../../shared/widgets/accessible_cards.dart';
import '../gestures/accessible_gesture_controller.dart';
import '../navigation/accessibility_router.dart';
import 'accessible_medicine_reader_screen.dart';

class AccessibleVerificationResultScreen extends StatefulWidget {
  final VerificationResult result;
  final TTSService ttsService;

  const AccessibleVerificationResultScreen({
    super.key,
    required this.result,
    required this.ttsService,
  });

  @override
  State<AccessibleVerificationResultScreen> createState() => _AccessibleVerificationResultScreenState();
}

class _AccessibleVerificationResultScreenState extends State<AccessibleVerificationResultScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _triggerHeadlineFeedback();
    });
  }

  void _triggerHeadlineFeedback() {
    final result = widget.result;

    // 1. Trigger distinct haptic pattern
    switch (result.status) {
      case VerificationStatus.authentic:
        HapticsService.verifiedAuthentic();
        break;
      case VerificationStatus.expired:
        HapticsService.expiredWarning();
        break;
      case VerificationStatus.suspectedCounterfeit:
      case VerificationStatus.recalled:
        HapticsService.suspiciousAlert();
        break;
      case VerificationStatus.revoked:
        HapticsService.expiredWarning();
        break;
      case VerificationStatus.offlineError:
      case VerificationStatus.invalid:
      default:
        HapticsService.invalidCode();
    }

    // 2. Speak calm, clear voice headline
    widget.ttsService.speak(result.toSpokenHeadline());
  }

  Color _getStatusColor() {
    switch (widget.result.status) {
      case VerificationStatus.authentic:
        return AccessibilityTheme.success;
      case VerificationStatus.expired:
        return AccessibilityTheme.warning;
      case VerificationStatus.suspectedCounterfeit:
      case VerificationStatus.recalled:
      case VerificationStatus.revoked:
        return AccessibilityTheme.error;
      case VerificationStatus.offlineError:
      case VerificationStatus.invalid:
      default:
        return Colors.grey;
    }
  }

  IconData _getStatusIcon() {
    switch (widget.result.status) {
      case VerificationStatus.authentic:
        return Icons.verified;
      case VerificationStatus.expired:
        return Icons.event_busy;
      case VerificationStatus.suspectedCounterfeit:
      case VerificationStatus.recalled:
      case VerificationStatus.revoked:
        return Icons.warning_amber_rounded;
      case VerificationStatus.offlineError:
        return Icons.wifi_off;
      case VerificationStatus.invalid:
      default:
        return Icons.error_outline;
    }
  }

  void _openDetailedReader() {
    Navigator.push(
      context,
      AccessibilityRouter.createAccessibleRoute(
        AccessibleMedicineReaderScreen(
          verificationResult: widget.result,
          ttsService: widget.ttsService,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final result = widget.result;
    final med = result.medicine;
    final statusColor = _getStatusColor();
    final statusIcon = _getStatusIcon();

    return AccessibleGestureController(
      ttsService: widget.ttsService,
      onDoubleTapScan: _openDetailedReader,
      onSwipeUpHome: () => Navigator.popUntil(context, (route) => route.isFirst),
      onSwipeDownRepeat: _triggerHeadlineFeedback,
      child: Scaffold(
        backgroundColor: AccessibilityTheme.background,
        appBar: AppBar(
          title: const Text('Verification Result'),
          backgroundColor: AccessibilityTheme.background,
        ),
        body: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // High-Contrast Verification Status Banner
              TalkBackSemantics(
                label: result.toSpokenHeadline(),
                isHeader: true,
                child: Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    color: statusColor.withOpacity(0.18),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: statusColor, width: 3),
                  ),
                  child: Column(
                    children: [
                      Icon(statusIcon, size: 64, color: statusColor),
                      const SizedBox(height: 12),
                      VerificationStatusBadge(
                        statusText: result.status.name.replaceAll('suspectedCounterfeit', 'SUSPECTED COUNTERFEIT').toUpperCase(),
                        backgroundColor: statusColor,
                      ),
                      const SizedBox(height: 12),
                      Text(
                        result.message,
                        textAlign: TextAlign.center,
                        style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AccessibilityTheme.textPrimary),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 20),

              // Medicine Headline Summary Card
              if (med != null) ...[
                TalkBackSemantics(
                  label: 'Medicine Summary: ${med.name}. Strength: ${med.dosage}. Manufacturer: ${med.manufacturer}.',
                  child: Container(
                    padding: const EdgeInsets.all(18),
                    decoration: BoxDecoration(
                      color: AccessibilityTheme.surface,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AccessibilityTheme.surfaceHighlight),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          med.name.toUpperCase(),
                          style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w800, color: AccessibilityTheme.accessibilityHighlight),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          'Dosage Strength: ${med.dosage}',
                          style: const TextStyle(fontSize: 18, color: AccessibilityTheme.textPrimary, fontWeight: FontWeight.w600),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Manufacturer: ${med.manufacturer}',
                          style: const TextStyle(fontSize: 16, color: AccessibilityTheme.textSecondary),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 20),
              ],

              const Spacer(),

              // Primary Action: Open Voice-First Detailed Reader
              AccessiblePrimaryButton(
                label: 'READ DETAILED MEDICINE INFO',
                semanticHint: 'Double tap to open voice-guided sequential medicine reader',
                icon: Icons.volume_up,
                height: 72,
                backgroundColor: AccessibilityTheme.accessibilityHighlight,
                onPressed: _openDetailedReader,
              ),
              const SizedBox(height: 14),

              // Secondary Action: Return Home
              AccessibleSecondaryButton(
                label: 'RETURN TO HOME',
                icon: Icons.home,
                onPressed: () => Navigator.popUntil(context, (route) => route.isFirst),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
