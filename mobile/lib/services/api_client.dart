import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../models/report.dart';
import 'auth_service.dart';

class ApiException implements Exception {
  ApiException(this.statusCode, this.message);

  final int statusCode;
  final String message;

  @override
  String toString() => 'ApiException($statusCode): $message';
}

/// Cliente HTTP de la API. Adjunta el token de Cognito en cada llamada y
/// traduce los errores de la API a excepciones tipadas para la capa de UI.
class ApiClient {
  ApiClient({
    required this.baseUrl,
    required AuthService auth,
    http.Client? httpClient,
  })  : _auth = auth,
        _http = httpClient ?? http.Client();

  final String baseUrl;
  final AuthService _auth;
  final http.Client _http;

  static const Duration _timeout = Duration(seconds: 20);

  Future<Map<String, String>> _headers() async => {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ${await _auth.accessToken()}',
      };

  Future<dynamic> _send(
    String method,
    String path, {
    Map<String, dynamic>? body,
    Map<String, String>? query,
  }) async {
    final uri = Uri.parse('$baseUrl$path').replace(queryParameters: query);
    final headers = await _headers();

    late http.Response res;
    try {
      final request = switch (method) {
        'GET' => _http.get(uri, headers: headers),
        'POST' => _http.post(uri, headers: headers, body: jsonEncode(body ?? {})),
        'PATCH' => _http.patch(uri, headers: headers, body: jsonEncode(body ?? {})),
        _ => throw ArgumentError('método no soportado: $method'),
      };
      res = await request.timeout(_timeout);
    } on SocketException {
      throw ApiException(0, 'Sin conexión. El reporte se guardó para enviarlo luego.');
    }

    if (res.statusCode >= 400) {
      final decoded = _tryDecode(res.body);
      throw ApiException(
        res.statusCode,
        decoded?['error']?.toString() ?? 'Error inesperado del servidor',
      );
    }
    return res.body.isEmpty ? null : jsonDecode(res.body);
  }

  Map<String, dynamic>? _tryDecode(String body) {
    try {
      return jsonDecode(body) as Map<String, dynamic>;
    } on FormatException {
      return null;
    }
  }

  Future<Report> createReport(Report report) async {
    final data = await _send('POST', '/reportes', body: report.toJson());
    return Report.fromJson(data as Map<String, dynamic>);
  }

  Future<Report> getReport(String id) async {
    final data = await _send('GET', '/reportes/$id');
    return Report.fromJson(data as Map<String, dynamic>);
  }

  Future<List<Hotspot>> hotspots(double lat, double lon) async {
    final data = await _send(
      'GET',
      '/puntos-criticos',
      query: {'lat': '$lat', 'lon': '$lon'},
    ) as Map<String, dynamic>;
    return (data['hotspots'] as List)
        .map((e) => Hotspot.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// Pide la URL prefirmada y sube la foto directamente a S3.
  /// La imagen nunca pasa por la API: menos latencia y menos costo.
  Future<String> uploadEvidence(File file, String contentType) async {
    final size = await file.length();
    final data = await _send(
      'POST',
      '/evidencias/url',
      body: {'content_type': contentType, 'size_bytes': size},
    ) as Map<String, dynamic>;

    // Las cabeceras las dicta el servidor: forman parte de la firma y dependen
    // de cómo esté cifrado el bucket en ese ambiente. La app no debe asumirlas.
    final required = (data['required_headers'] as Map?)?.map(
          (k, v) => MapEntry(k.toString(), v.toString()),
        ) ??
        {'Content-Type': contentType};

    final res = await _http.put(
      Uri.parse(data['upload_url'] as String),
      headers: required,
      body: await file.readAsBytes(),
    ).timeout(const Duration(seconds: 60));

    if (res.statusCode >= 400) {
      throw ApiException(res.statusCode, 'No se pudo subir la evidencia');
    }
    return data['evidence_key'] as String;
  }

  void dispose() => _http.close();
}
