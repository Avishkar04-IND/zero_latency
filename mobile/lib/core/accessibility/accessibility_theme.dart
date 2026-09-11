import 'package:flutter/material.dart';

/// Zero Latency Accessibility Design System & Color Palette
class AccessibilityTheme {
  // Brand & High-Contrast Colors
  static const Color background = Color(0xFF0B0F14);
  static const Color surface = Color(0xFF151B22);
  static const Color surfaceHighlight = Color(0xFF212B36);
  
  static const Color primary = Color(0xFF00E5FF); // Vibrant Cyan
  static const Color accessibilityHighlight = Color(0xFFFFD600); // High-visibility Yellow
  
  static const Color success = Color(0xFF00C853); // High-contrast Green
  static const Color warning = Color(0xFFFFB300); // Amber Warning
  static const Color error = Color(0xFFFF5252); // Red Alert
  
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xFFB8C1CC);
  static const Color textDark = Color(0xFF000000);

  static ThemeData get highContrastDarkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: background,
      colorScheme: const ColorScheme.dark(
        primary: primary,
        onPrimary: textDark,
        secondary: accessibilityHighlight,
        onSecondary: textDark,
        surface: surface,
        onSurface: textPrimary,
        error: error,
        onError: textPrimary,
      ),
      textTheme: const TextTheme(
        // App Title / Hero Header
        displayLarge: TextStyle(
          fontSize: 32,
          fontWeight: FontWeight.w800,
          color: accessibilityHighlight,
          height: 1.2,
          letterSpacing: 0.5,
        ),
        // Screen Title / Heading
        headlineLarge: TextStyle(
          fontSize: 26,
          fontWeight: FontWeight.bold,
          color: textPrimary,
          height: 1.25,
        ),
        // Section Header
        headlineMedium: TextStyle(
          fontSize: 22,
          fontWeight: FontWeight.bold,
          color: primary,
          height: 1.3,
        ),
        // Card Titles / Primary Actions
        titleLarge: TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.bold,
          color: textPrimary,
          height: 1.3,
        ),
        // Body Text
        bodyLarge: TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: textPrimary,
          height: 1.4,
        ),
        // Secondary / Subtitle Text
        bodyMedium: TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w500,
          color: textSecondary,
          height: 1.4,
        ),
        // Action Button Text
        labelLarge: TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.bold,
          color: textDark,
          letterSpacing: 0.5,
        ),
        // Accessibility Hint
        labelSmall: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w500,
          color: textSecondary,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: accessibilityHighlight,
          foregroundColor: textDark,
          minimumSize: const Size(double.infinity, 64),
          padding: const EdgeInsets.symmetric(vertical: 18, horizontal: 24),
          textStyle: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          elevation: 4,
        ),
      ),
      cardTheme: CardThemeData(
        color: surface,
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: surfaceHighlight, width: 1.5),
        ),
      ),
    );
  }
}
