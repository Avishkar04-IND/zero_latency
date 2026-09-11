import 'package:flutter/material.dart';

class AccessibilityTheme {
  static ThemeData get highContrastDarkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: const Color(0xFF000000), // Pure Black for maximum contrast
      colorScheme: const ColorScheme.dark(
        primary: Color(0xFFFFD700), // High-visibility Yellow
        onPrimary: Color(0xFF000000),
        secondary: Color(0xFF00FFFF), // High-contrast Cyan
        onSecondary: Color(0xFF000000),
        surface: Color(0xFF121212),
        onSurface: Color(0xFFFFFFFF),
        error: Color(0xFFFF3333), // High-visibility Red
        onError: Color(0xFFFFFFFF),
      ),
      textTheme: const TextTheme(
        displayLarge: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Color(0xFFFFD700)),
        headlineLarge: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Color(0xFFFFFFFF)),
        headlineMedium: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFFFFD700)),
        bodyLarge: TextStyle(fontSize: 22, fontWeight: FontWeight.w600, color: Color(0xFFFFFFFF)),
        bodyMedium: TextStyle(fontSize: 18, color: Color(0xFFE0E0E0)),
        labelLarge: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF000000)),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFFFFD700),
          foregroundColor: const Color(0xFF000000),
          minimumSize: const Size(double.infinity, 72), // Large touch target for motor accessibility
          padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 24),
          textStyle: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
      ),
    );
  }
}
