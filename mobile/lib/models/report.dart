/// Modelos de dominio de la app. Espejan el contrato de la API.
library;

enum WasteCategory {
  escombros('escombros', 'Escombros'),
  organicos('organicos', 'Orgánicos'),
  reciclables('reciclables', 'Reciclables'),
  voluminosos('voluminosos', 'Voluminosos'),
  peligrosos('peligrosos', 'Peligrosos'),
  noClasificado('no_clasificado', 'Sin clasificar');

  const WasteCategory(this.value, this.label);

  final String value;
  final String label;

  static WasteCategory fromValue(String? raw) => WasteCategory.values.firstWhere(
        (c) => c.value == raw,
        orElse: () => WasteCategory.noClasificado,
      );
}

enum ReportStatus {
  reportado('reportado', 'Reportado'),
  verificado('verificado', 'Verificado'),
  programado('programado', 'Programado'),
  atendido('atendido', 'Atendido'),
  descartado('descartado', 'Descartado');

  const ReportStatus(this.value, this.label);

  final String value;
  final String label;

  static ReportStatus fromValue(String? raw) => ReportStatus.values.firstWhere(
        (s) => s.value == raw,
        orElse: () => ReportStatus.reportado,
      );
}

class Report {
  const Report({
    required this.reportId,
    required this.lat,
    required this.lon,
    required this.category,
    required this.severity,
    required this.status,
    required this.createdAt,
    this.description = '',
    this.evidenceKey,
    this.aiLabels = const [],
  });

  final String reportId;
  final double lat;
  final double lon;
  final WasteCategory category;
  final int severity;
  final ReportStatus status;
  final DateTime createdAt;
  final String description;
  final String? evidenceKey;
  final List<String> aiLabels;

  factory Report.fromJson(Map<String, dynamic> json) => Report(
        reportId: json['report_id'] as String,
        lat: (json['lat'] as num).toDouble(),
        lon: (json['lon'] as num).toDouble(),
        category: WasteCategory.fromValue(json['category'] as String?),
        severity: (json['severity'] as num?)?.toInt() ?? 1,
        status: ReportStatus.fromValue(json['status'] as String?),
        createdAt:
            DateTime.tryParse(json['created_at'] as String? ?? '') ?? DateTime.now(),
        description: json['description'] as String? ?? '',
        evidenceKey: json['evidence_key'] as String?,
        aiLabels: ((json['ai_labels'] as List?) ?? const [])
            .map((e) => e.toString())
            .toList(),
      );

  Map<String, dynamic> toJson() => {
        'lat': lat,
        'lon': lon,
        'category': category.value,
        'severity': severity,
        'description': description,
        if (evidenceKey != null) 'evidence_key': evidenceKey,
      };
}

class Hotspot {
  const Hotspot({
    required this.lat,
    required this.lon,
    required this.reportCount,
    required this.severityScore,
    required this.dominantCategory,
  });

  final double lat;
  final double lon;
  final int reportCount;
  final int severityScore;
  final WasteCategory dominantCategory;

  factory Hotspot.fromJson(Map<String, dynamic> json) {
    final centroid = json['centroid'] as Map<String, dynamic>;
    return Hotspot(
      lat: (centroid['lat'] as num).toDouble(),
      lon: (centroid['lon'] as num).toDouble(),
      reportCount: (json['report_count'] as num).toInt(),
      severityScore: (json['severity_score'] as num).toInt(),
      dominantCategory:
          WasteCategory.fromValue(json['dominant_category'] as String?),
    );
  }

  /// Prioridad operativa derivada de la severidad acumulada del grupo.
  String get priority {
    if (severityScore >= 15) return 'Alta';
    if (severityScore >= 8) return 'Media';
    return 'Baja';
  }
}
