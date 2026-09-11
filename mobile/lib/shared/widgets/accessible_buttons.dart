import 'package:flutter/material.dart';
import '../../core/accessibility/accessibility_theme.dart';
import '../../services/haptics/haptics_service.dart';

/// Primary Accessibility Action Button (Height 64-80px)
class AccessiblePrimaryButton extends StatelessWidget {
  final String label;
  final String? semanticHint;
  final IconData? icon;
  final VoidCallback onPressed;
  final Color backgroundColor;
  final Color foregroundColor;
  final double height;

  const AccessiblePrimaryButton({
    super.key,
    required this.label,
    this.semanticHint,
    this.icon,
    required this.onPressed,
    this.backgroundColor = AccessibilityTheme.accessibilityHighlight,
    this.foregroundColor = AccessibilityTheme.textDark,
    this.height = 72.0,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: label,
      hint: semanticHint ?? 'Double tap to activate $label',
      button: true,
      enabled: true,
      child: SizedBox(
        height: height,
        width: double.infinity,
        child: ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: backgroundColor,
            foregroundColor: foregroundColor,
            elevation: 4,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          ),
          onPressed: () {
            HapticsService.capture();
            onPressed();
          },
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (icon != null) ...[
                Icon(icon, size: 32, color: foregroundColor),
                const SizedBox(width: 12),
              ],
              Flexible(
                child: Text(
                  label.toUpperCase(),
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: foregroundColor,
                    letterSpacing: 0.5,
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

/// Secondary Accessibility Button (Min 48px height)
class AccessibleSecondaryButton extends StatelessWidget {
  final String label;
  final String? semanticHint;
  final IconData? icon;
  final VoidCallback onPressed;

  const AccessibleSecondaryButton({
    super.key,
    required this.label,
    this.semanticHint,
    this.icon,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: label,
      hint: semanticHint ?? 'Double tap to open $label',
      button: true,
      child: SizedBox(
        height: 56,
        width: double.infinity,
        child: OutlinedButton(
          style: OutlinedButton.styleFrom(
            side: const BorderSide(color: AccessibilityTheme.primary, width: 2),
            foregroundColor: AccessibilityTheme.textPrimary,
            backgroundColor: AccessibilityTheme.surface,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          ),
          onPressed: () {
            HapticsService.scanningTick();
            onPressed();
          },
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (icon != null) ...[
                Icon(icon, size: 26, color: AccessibilityTheme.primary),
                const SizedBox(width: 10),
              ],
              Text(
                label,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: AccessibilityTheme.textPrimary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Accessible Icon Button with Minimum 48x48 Touch Target
class AccessibleIconButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final String? hint;
  final VoidCallback onPressed;
  final Color color;

  const AccessibleIconButton({
    super.key,
    required this.icon,
    required this.label,
    this.hint,
    required this.onPressed,
    this.color = AccessibilityTheme.primary,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: label,
      hint: hint ?? 'Double tap to activate',
      button: true,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(12),
          onTap: () {
            HapticsService.scanningTick();
            onPressed();
          },
          child: Container(
            constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AccessibilityTheme.surfaceHighlight,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: color.withOpacity(0.5), width: 1.5),
            ),
            child: Icon(icon, size: 28, color: color),
          ),
        ),
      ),
    );
  }
}

/// Voice Action Microphone Button with Pulsing Highlight
class VoiceActionButton extends StatelessWidget {
  final String label;
  final bool isListening;
  final VoidCallback onPressed;

  const VoiceActionButton({
    super.key,
    required this.label,
    required this.isListening,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: isListening ? 'Listening. Tap to stop microphone.' : label,
      hint: 'Double tap or long press to activate voice microphone',
      button: true,
      child: SizedBox(
        height: 72,
        width: double.infinity,
        child: ElevatedButton.icon(
          style: ElevatedButton.styleFrom(
            backgroundColor: isListening ? AccessibilityTheme.error : AccessibilityTheme.primary,
            foregroundColor: AccessibilityTheme.textDark,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            elevation: 4,
          ),
          onPressed: () {
            HapticsService.codeDetected();
            onPressed();
          },
          icon: Icon(
            isListening ? Icons.mic_off : Icons.mic,
            size: 32,
            color: AccessibilityTheme.textDark,
          ),
          label: Text(
            isListening ? 'STOP LISTENING' : label.toUpperCase(),
            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AccessibilityTheme.textDark),
          ),
        ),
      ),
    );
  }
}
