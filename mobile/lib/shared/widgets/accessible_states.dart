import 'package:flutter/material.dart';
import '../../core/accessibility/accessibility_theme.dart';
import 'accessible_buttons.dart';

/// Loading View with Screen Reader Semantics
class AccessibleLoadingState extends StatelessWidget {
  final String message;

  const AccessibleLoadingState({
    super.key,
    this.message = 'Loading data. Please wait.',
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: message,
      liveRegion: true,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const SizedBox(
              width: 56,
              height: 56,
              child: CircularProgressIndicator(
                strokeWidth: 5,
                color: AccessibilityTheme.accessibilityHighlight,
              ),
            ),
            const SizedBox(height: 24),
            Text(
              message,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: AccessibilityTheme.textPrimary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Error View with Action Retry
class AccessibleErrorState extends StatelessWidget {
  final String title;
  final String message;
  final VoidCallback onRetry;

  const AccessibleErrorState({
    super.key,
    this.title = 'An Error Occurred',
    required this.message,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: '$title. $message. Double tap retry button below.',
      liveRegion: true,
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 72, color: AccessibilityTheme.error),
              const SizedBox(height: 16),
              Text(
                title,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AccessibilityTheme.error),
              ),
              const SizedBox(height: 8),
              Text(
                message,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 18, color: AccessibilityTheme.textSecondary),
              ),
              const SizedBox(height: 32),
              AccessiblePrimaryButton(
                label: 'RETRY ACTION',
                icon: Icons.refresh,
                onPressed: onRetry,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Empty State View with Semantics
class AccessibleEmptyState extends StatelessWidget {
  final String title;
  final String message;
  final IconData icon;
  final String? actionLabel;
  final VoidCallback? onAction;

  const AccessibleEmptyState({
    super.key,
    required this.title,
    required this.message,
    this.icon = Icons.inbox_outlined,
    this.actionLabel,
    this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: '$title. $message',
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 64, color: AccessibilityTheme.primary),
              const SizedBox(height: 16),
              Text(
                title,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AccessibilityTheme.textPrimary),
              ),
              const SizedBox(height: 8),
              Text(
                message,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 16, color: AccessibilityTheme.textSecondary),
              ),
              if (actionLabel != null && onAction != null) ...[
                const SizedBox(height: 24),
                AccessibleSecondaryButton(
                  label: actionLabel!,
                  onPressed: onAction!,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
