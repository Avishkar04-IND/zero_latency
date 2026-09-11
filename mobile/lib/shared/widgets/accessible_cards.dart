import 'package:flutter/material.dart';
import '../../core/accessibility/accessibility_theme.dart';
import '../../services/haptics/haptics_service.dart';

/// Reusable Accessible Card Container
class AccessibleCard extends StatelessWidget {
  final String label;
  final String? hint;
  final String title;
  final String? subtitle;
  final IconData icon;
  final Color accentColor;
  final VoidCallback onTap;

  const AccessibleCard({
    super.key,
    required this.label,
    this.hint,
    required this.title,
    this.subtitle,
    required this.icon,
    this.accentColor = AccessibilityTheme.primary,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: label,
      hint: hint ?? 'Double tap to open $title',
      button: true,
      child: Material(
        color: AccessibilityTheme.surface,
        borderRadius: BorderRadius.circular(16),
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: () {
            HapticsService.scanningTick();
            onTap();
          },
          child: Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: accentColor.withOpacity(0.4), width: 1.5),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: accentColor.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(icon, size: 36, color: accentColor),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: AccessibilityTheme.textPrimary,
                        ),
                      ),
                      if (subtitle != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          subtitle!,
                          style: const TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w500,
                            color: AccessibilityTheme.textSecondary,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
                const Icon(Icons.arrow_forward_ios, size: 20, color: AccessibilityTheme.textSecondary),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Status Banner Card for Notifications & State Alerts
class StatusCard extends StatelessWidget {
  final String title;
  final String message;
  final IconData icon;
  final Color color;

  const StatusCard({
    super.key,
    required this.title,
    required this.message,
    this.icon = Icons.info_outline,
    this.color = AccessibilityTheme.primary,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: '$title. $message',
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: color.withOpacity(0.12),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: color, width: 1.5),
        ),
        child: Row(
          children: [
            Icon(icon, size: 32, color: color),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: color),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    message,
                    style: const TextStyle(fontSize: 15, color: AccessibilityTheme.textPrimary),
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

/// Verification Status Badge / Pill
class VerificationStatusBadge extends StatelessWidget {
  final String statusText;
  final Color backgroundColor;
  final Color textColor;

  const VerificationStatusBadge({
    super.key,
    required this.statusText,
    required this.backgroundColor,
    this.textColor = AccessibilityTheme.textDark,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'Verification Status: $statusText',
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: backgroundColor,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          statusText.toUpperCase(),
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: textColor,
            letterSpacing: 0.5,
          ),
        ),
      ),
    );
  }
}

/// Voice Guidance Control & Indicator Banner
class VoiceGuidanceBanner extends StatelessWidget {
  final bool isVoiceEnabled;
  final VoidCallback onRepeatPressed;
  final VoidCallback onToggleVoice;

  const VoiceGuidanceBanner({
    super.key,
    required this.isVoiceEnabled,
    required this.onRepeatPressed,
    required this.onToggleVoice,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      decoration: BoxDecoration(
        color: AccessibilityTheme.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AccessibilityTheme.surfaceHighlight),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Icon(
                isVoiceEnabled ? Icons.volume_up : Icons.volume_off,
                size: 24,
                color: isVoiceEnabled ? AccessibilityTheme.accessibilityHighlight : AccessibilityTheme.textSecondary,
              ),
              const SizedBox(width: 8),
              Text(
                isVoiceEnabled ? 'Voice Guidance Active' : 'Voice Muted',
                style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AccessibilityTheme.textPrimary),
              ),
            ],
          ),
          Row(
            children: [
              Semantics(
                label: 'Repeat Audio Prompt',
                button: true,
                child: IconButton(
                  icon: const Icon(Icons.replay, color: AccessibilityTheme.primary),
                  onPressed: () {
                    HapticsService.scanningTick();
                    onRepeatPressed();
                  },
                ),
              ),
              Semantics(
                label: isVoiceEnabled ? 'Mute Voice Guidance' : 'Enable Voice Guidance',
                button: true,
                child: IconButton(
                  icon: Icon(
                    isVoiceEnabled ? Icons.volume_up_outlined : Icons.volume_off_outlined,
                    color: isVoiceEnabled ? AccessibilityTheme.accessibilityHighlight : Colors.grey,
                  ),
                  onPressed: () {
                    HapticsService.scanningTick();
                    onToggleVoice();
                  },
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
