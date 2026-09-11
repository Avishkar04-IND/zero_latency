import 'package:flutter/material.dart';
import '../../../core/accessibility/accessibility_theme.dart';
import '../../../core/accessibility/talkback_helpers.dart';
import 'medicine_reader_controller.dart';

class MedicineInformationSectionWidget extends StatelessWidget {
  final MedicineReaderSectionData section;
  final bool isActive;
  final VoidCallback onTap;

  const MedicineInformationSectionWidget({
    super.key,
    required this.section,
    required this.isActive,
    required this.onTap,
  });

  IconData _getIconForTitle(String title) {
    switch (title.toUpperCase()) {
      case 'MEDICINE NAME':
        return Icons.medication;
      case 'GENERIC NAME':
        return Icons.label_important_outline;
      case 'STRENGTH':
        return Icons.fitness_center;
      case 'MANUFACTURER':
        return Icons.factory_outlined;
      case 'BATCH NUMBER':
        return Icons.inventory_2_outlined;
      case 'MANUFACTURING DATE':
        return Icons.calendar_today;
      case 'EXPIRY DATE':
        return Icons.event_busy;
      case 'USES':
        return Icons.medical_services_outlined;
      case 'WARNINGS':
        return Icons.warning_amber_rounded;
      case 'STORAGE INSTRUCTIONS':
        return Icons.ac_unit_outlined;
      default:
        return Icons.info_outline;
    }
  }

  @override
  Widget build(BuildContext context) {
    final icon = _getIconForTitle(section.title);
    final borderColor = isActive ? AccessibilityTheme.accessibilityHighlight : AccessibilityTheme.surfaceHighlight;

    return TalkBackSemantics(
      label: '${section.title}. ${section.content}',
      hint: 'Double tap to read this section aloud',
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        margin: const EdgeInsets.only(bottom: 14),
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: isActive ? AccessibilityTheme.surfaceHighlight : AccessibilityTheme.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: borderColor,
            width: isActive ? 3.0 : 1.5,
          ),
          boxShadow: isActive
              ? [
                  BoxShadow(
                    color: AccessibilityTheme.accessibilityHighlight.withOpacity(0.25),
                    blurRadius: 10,
                    spreadRadius: 1,
                  )
                ]
              : null,
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: isActive ? AccessibilityTheme.accessibilityHighlight : AccessibilityTheme.primary.withOpacity(0.15),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                icon,
                size: 32,
                color: isActive ? Colors.black : AccessibilityTheme.primary,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    section.title,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: isActive ? AccessibilityTheme.accessibilityHighlight : AccessibilityTheme.textSecondary,
                      letterSpacing: 0.5,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    section.content,
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: AccessibilityTheme.textPrimary,
                      height: 1.3,
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
