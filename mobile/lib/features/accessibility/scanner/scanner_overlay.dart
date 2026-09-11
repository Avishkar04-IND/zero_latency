import 'package:flutter/material.dart';
import '../../../core/accessibility/accessibility_theme.dart';
import '../../../core/accessibility/talkback_helpers.dart';
import 'scanner_state.dart';
import 'scanner_guidance.dart';

class ScannerOverlay extends StatelessWidget {
  final ScannerState state;
  final VoidCallback onToggleTorch;
  final VoidCallback onSimulateScan;
  final VoidCallback onHelp;

  const ScannerOverlay({
    super.key,
    required this.state,
    required this.onToggleTorch,
    required this.onSimulateScan,
    required this.onHelp,
  });

  @override
  Widget build(BuildContext context) {
    final guidanceText = ScannerGuidanceEngine.getGuidanceMessage(state);
    final isDetected = state.status == ScannerStatus.codeDetected || state.status == ScannerStatus.verifying;

    return Column(
      children: [
        // Top Guidance Banner
        TalkBackSemantics(
          label: guidanceText,
          isHeader: true,
          child: Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 20),
            color: isDetected ? AccessibilityTheme.success : AccessibilityTheme.surface,
            child: Row(
              children: [
                Icon(
                  isDetected ? Icons.check_circle_outline : Icons.search,
                  color: isDetected ? Colors.black : AccessibilityTheme.accessibilityHighlight,
                  size: 32,
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Text(
                    guidanceText,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: isDetected ? Colors.black : AccessibilityTheme.textPrimary,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),

        // Middle Viewport Scan Target Reticle Box
        Expanded(
          child: Center(
            child: Semantics(
              label: 'Medicine Scanner Viewport. Align medicine package code inside box.',
              child: Container(
                width: 270,
                height: 270,
                decoration: BoxDecoration(
                  border: Border.all(
                    color: isDetected ? AccessibilityTheme.success : AccessibilityTheme.accessibilityHighlight,
                    width: isDetected ? 6 : 4,
                  ),
                  borderRadius: BorderRadius.circular(24),
                  color: Colors.black.withOpacity(0.2),
                ),
                child: Center(
                  child: Icon(
                    Icons.qr_code_scanner,
                    size: 80,
                    color: isDetected ? AccessibilityTheme.success : AccessibilityTheme.primary.withOpacity(0.8),
                  ),
                ),
              ),
            ),
          ),
        ),

        // Bottom Action Control Bar
        Container(
          padding: const EdgeInsets.all(16),
          color: AccessibilityTheme.background,
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  TalkBackSemantics(
                    label: state.isTorchOn ? 'Turn Flashlight Off' : 'Turn Flashlight On',
                    hint: 'Toggles camera torch light',
                    onTap: onToggleTorch,
                    child: Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: state.isTorchOn ? AccessibilityTheme.accessibilityHighlight : AccessibilityTheme.surface,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: AccessibilityTheme.primary),
                      ),
                      child: Icon(
                        state.isTorchOn ? Icons.flash_on : Icons.flash_off,
                        color: state.isTorchOn ? Colors.black : AccessibilityTheme.primary,
                        size: 32,
                      ),
                    ),
                  ),
                  TalkBackSemantics(
                    label: 'Scanner Help Guide',
                    hint: 'Opens gesture and scanner guidance help',
                    onTap: onHelp,
                    child: Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: AccessibilityTheme.surface,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: AccessibilityTheme.primary),
                      ),
                      child: const Icon(Icons.help_outline, color: AccessibilityTheme.primary, size: 32),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AccessibilityTheme.accessibilityHighlight,
                  foregroundColor: Colors.black,
                  minimumSize: const Size(double.infinity, 60),
                ),
                onPressed: onSimulateScan,
                icon: const Icon(Icons.center_focus_strong, size: 28),
                label: const Text('TEST / SIMULATE CODE SCAN'),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
