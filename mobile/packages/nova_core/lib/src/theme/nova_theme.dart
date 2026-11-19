import 'package:flutter/material.dart';

class NovaColors {
  static const red = Color(0xFFD71920);
  static const redDark = Color(0xFFB51219);
  static const charcoal = Color(0xFF262B31);
  static const charcoalSoft = Color(0xFF3B424A);
  static const ink = Color(0xFF20252B);
  static const muted = Color(0xFF727A84);
  static const border = Color(0xFFE7E9EC);
  static const surface = Color(0xFFF6F7F8);
  static const white = Colors.white;
}

class NovaTheme {
  static ThemeData get light {
    final scheme = ColorScheme.fromSeed(
      seedColor: NovaColors.red,
      primary: NovaColors.red,
      secondary: NovaColors.charcoal,
      surface: NovaColors.white,
      error: const Color(0xFFB3261E),
      brightness: Brightness.light,
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: NovaColors.surface,
      fontFamily: 'Roboto',
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.white,
        foregroundColor: NovaColors.ink,
        elevation: 0,
        centerTitle: false,
        surfaceTintColor: Colors.transparent,
        titleTextStyle: TextStyle(fontSize: 19, fontWeight: FontWeight.w800, color: NovaColors.ink),
      ),
      cardTheme: CardThemeData(
        color: Colors.white,
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(18),
          side: const BorderSide(color: NovaColors.border),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        hintStyle: const TextStyle(color: NovaColors.muted),
        contentPadding: const EdgeInsets.symmetric(horizontal: 15, vertical: 15),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(13), borderSide: const BorderSide(color: NovaColors.border)),
        enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(13), borderSide: const BorderSide(color: NovaColors.border)),
        focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(13), borderSide: const BorderSide(color: NovaColors.red, width: 1.5)),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: NovaColors.red,
          foregroundColor: Colors.white,
          minimumSize: const Size(48, 50),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(13)),
          textStyle: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: NovaColors.charcoal,
          side: const BorderSide(color: NovaColors.border),
          minimumSize: const Size(44, 46),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(13)),
        ),
      ),
      textTheme: const TextTheme(
        headlineSmall: TextStyle(fontSize: 24, height: 1.15, fontWeight: FontWeight.w900, color: NovaColors.ink),
        titleLarge: TextStyle(fontSize: 19, fontWeight: FontWeight.w800, color: NovaColors.ink),
        titleMedium: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: NovaColors.ink),
        bodyLarge: TextStyle(fontSize: 15, color: NovaColors.ink),
        bodyMedium: TextStyle(fontSize: 13, color: NovaColors.charcoalSoft),
        bodySmall: TextStyle(fontSize: 11, color: NovaColors.muted),
      ),
      dividerColor: NovaColors.border,
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: NovaColors.charcoal,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }
}
