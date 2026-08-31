import 'package:flutter/material.dart';

/// Tema único de la app. Centralizarlo evita colores dispersos por las
/// pantallas y garantiza contraste accesible (WCAG AA) en ambos modos.
class EcoTheme {
  static const seed = Color(0xFF2E7D5B);

  static ThemeData light() => _base(Brightness.light);
  static ThemeData dark() => _base(Brightness.dark);

  static ThemeData _base(Brightness brightness) {
    final scheme = ColorScheme.fromSeed(seedColor: seed, brightness: brightness);
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      appBarTheme: AppBarTheme(
        centerTitle: true,
        backgroundColor: scheme.surface,
        surfaceTintColor: scheme.surfaceTint,
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size.fromHeight(52), // objetivo táctil amplio
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      ),
      inputDecorationTheme: const InputDecorationTheme(
        border: OutlineInputBorder(),
        filled: true,
      ),
      cardTheme: CardTheme(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(color: scheme.outlineVariant),
        ),
      ),
    );
  }

  static Color severityColor(int severity, ColorScheme scheme) => switch (severity) {
        >= 5 => const Color(0xFFB3261E),
        4 => const Color(0xFFE65100),
        3 => const Color(0xFFF9A825),
        _ => scheme.primary,
      };
}
