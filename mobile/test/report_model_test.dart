import 'package:ecoruta/models/report.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('WasteCategory', () {
    test('mapea valor conocido', () {
      expect(WasteCategory.fromValue('escombros'), WasteCategory.escombros);
    });

    test('valor desconocido cae en no_clasificado', () {
      expect(WasteCategory.fromValue('basura'), WasteCategory.noClasificado);
      expect(WasteCategory.fromValue(null), WasteCategory.noClasificado);
    });
  });

  group('Report', () {
    final json = {
      'report_id': 'r-1',
      'lat': 4.710989,
      'lon': -74.072092,
      'category': 'escombros',
      'severity': 4,
      'status': 'verificado',
      'created_at': '2026-08-31T12:00:00+00:00',
      'description': 'andén bloqueado',
      'ai_labels': ['Rubble', 'Brick'],
    };

    test('deserializa completo', () {
      final report = Report.fromJson(json);
      expect(report.reportId, 'r-1');
      expect(report.category, WasteCategory.escombros);
      expect(report.status, ReportStatus.verificado);
      expect(report.aiLabels, ['Rubble', 'Brick']);
    });

    test('tolera campos opcionales ausentes', () {
      final report = Report.fromJson({
        'report_id': 'r-2',
        'lat': 4.0,
        'lon': -74.0,
      });
      expect(report.severity, 1);
      expect(report.description, isEmpty);
      expect(report.aiLabels, isEmpty);
    });

    test('toJson no envía campos que asigna el servidor', () {
      final payload = Report.fromJson(json).toJson();
      expect(payload.containsKey('report_id'), isFalse);
      expect(payload.containsKey('status'), isFalse);
      expect(payload['category'], 'escombros');
    });
  });

  group('Hotspot', () {
    Hotspot build(int score) => Hotspot.fromJson({
          'centroid': {'lat': 4.71, 'lon': -74.07},
          'report_count': 5,
          'severity_score': score,
          'dominant_category': 'peligrosos',
        });

    test('clasifica prioridad', () {
      expect(build(20).priority, 'Alta');
      expect(build(10).priority, 'Media');
      expect(build(4).priority, 'Baja');
    });

    test('lee el centroide', () {
      expect(build(10).lat, 4.71);
      expect(build(10).dominantCategory, WasteCategory.peligrosos);
    });
  });
}
