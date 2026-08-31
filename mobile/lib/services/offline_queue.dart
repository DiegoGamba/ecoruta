import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import '../models/report.dart';
import 'api_client.dart';

/// Cola de reportes pendientes de envío.
///
/// Motivación de campo: los puntos críticos suelen estar en zonas periféricas
/// con conectividad intermitente. Si el envío falla, el reporte se persiste
/// localmente y se reintenta cuando vuelve la red, de modo que el ciudadano
/// nunca pierde el trabajo de capturar la evidencia.
class OfflineQueue {
  OfflineQueue(this._api);

  static const _key = 'reportes_pendientes';
  final ApiClient _api;

  Future<void> enqueue(Report report) async {
    final prefs = await SharedPreferences.getInstance();
    final pending = prefs.getStringList(_key) ?? <String>[];
    pending.add(jsonEncode(report.toJson()));
    await prefs.setStringList(_key, pending);
  }

  Future<int> pendingCount() async {
    final prefs = await SharedPreferences.getInstance();
    return (prefs.getStringList(_key) ?? const <String>[]).length;
  }

  /// Reintenta la cola completa y devuelve cuántos reportes se sincronizaron.
  /// Los que fallan por red se conservan; los rechazados por validación (4xx)
  /// se descartan para no bloquear la cola indefinidamente.
  Future<int> flush() async {
    final prefs = await SharedPreferences.getInstance();
    final pending = prefs.getStringList(_key) ?? <String>[];
    if (pending.isEmpty) return 0;

    final remaining = <String>[];
    var sent = 0;

    for (final raw in pending) {
      final json = jsonDecode(raw) as Map<String, dynamic>;
      try {
        await _api.createReport(
          Report.fromJson({
            ...json,
            'report_id': 'pendiente',
            'status': 'reportado',
            'created_at': DateTime.now().toIso8601String(),
          }),
        );
        sent++;
      } on ApiException catch (e) {
        if (e.statusCode == 0 || e.statusCode >= 500) {
          remaining.add(raw); // problema transitorio: se reintenta después
        }
      }
    }

    await prefs.setStringList(_key, remaining);
    return sent;
  }
}
