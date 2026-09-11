import 'package:flutter/material.dart';
import '../../../services/tts/tts_service.dart';
import '../../../services/api/api_service.dart';
import '../../../shared/models/verification_model.dart';
import '../home/accessible_home_screen.dart';
import '../scanner/accessible_scanner_screen.dart';
import '../medicine/accessible_verification_result_screen.dart';
import '../medicine/accessible_medicine_reader_screen.dart';
import '../assistant/accessible_assistant_screen.dart';
import '../history/accessible_history_screen.dart';
import '../settings/accessible_settings_screen.dart';
import '../help/accessible_help_screen.dart';

class AccessibilityRouter {
  static Route createAccessibleRoute(Widget page) {
    return PageRouteBuilder(
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionDuration: const Duration(milliseconds: 200),
      reverseTransitionDuration: const Duration(milliseconds: 180),
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        final fadeAnimation = CurvedAnimation(parent: animation, curve: Curves.easeInOut);
        return FadeTransition(
          opacity: fadeAnimation,
          child: child,
        );
      },
    );
  }

  static void navigateToScanner(BuildContext context, TTSService tts, ApiService api) {
    Navigator.push(
      context,
      createAccessibleRoute(AccessibleScannerScreen(ttsService: tts, apiService: api)),
    );
  }

  static void navigateToAssistant(BuildContext context, TTSService tts, ApiService api, {VerificationResult? verificationResult}) {
    Navigator.push(
      context,
      createAccessibleRoute(AccessibleAssistantScreen(
        ttsService: tts,
        apiService: api,
        verificationResult: verificationResult,
      )),
    );
  }

  static void navigateToHistory(BuildContext context, TTSService tts, ApiService api) {
    Navigator.push(
      context,
      createAccessibleRoute(AccessibleHistoryScreen(ttsService: tts, apiService: api)),
    );
  }

  static void navigateToSettings(BuildContext context, TTSService tts) {
    Navigator.push(
      context,
      createAccessibleRoute(AccessibleSettingsScreen(ttsService: tts)),
    );
  }

  static void navigateToHelp(BuildContext context, TTSService tts) {
    Navigator.push(
      context,
      createAccessibleRoute(AccessibleHelpScreen(ttsService: tts)),
    );
  }

  static void navigateToVerificationResult(BuildContext context, TTSService tts, VerificationResult result) {
    Navigator.push(
      context,
      createAccessibleRoute(AccessibleVerificationResultScreen(result: result, ttsService: tts)),
    );
  }

  static void navigateToMedicineReader(BuildContext context, TTSService tts, VerificationResult result) {
    Navigator.push(
      context,
      createAccessibleRoute(AccessibleMedicineReaderScreen(verificationResult: result, ttsService: tts)),
    );
  }
}
