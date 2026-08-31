import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../models/report.dart';
import '../services/api_client.dart';
import '../services/location_service.dart';

/// Mapa de puntos críticos. El tamaño y el color del marcador comunican la
/// prioridad de un vistazo, que es lo que necesita el operador en campo.
class MapScreen extends StatefulWidget {
  const MapScreen({super.key, required this.api, required this.location});

  final ApiClient api;
  final LocationService location;

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  static const _bogota = LatLng(4.710989, -74.072092);

  List<Hotspot> _hotspots = const [];
  LatLng _center = _bogota;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      try {
        final pos = await widget.location.current();
        _center = LatLng(pos.latitude, pos.longitude);
      } on LocationDeniedException {
        _center = _bogota; // degradación elegante: se muestra la ciudad
      }
      final data = await widget.api.hotspots(_center.latitude, _center.longitude);
      if (mounted) setState(() => _hotspots = data);
    } on ApiException catch (e) {
      if (mounted) setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Puntos críticos'),
        actions: [
          IconButton(
            onPressed: _loading ? null : _load,
            icon: const Icon(Icons.refresh),
            tooltip: 'Actualizar',
          ),
        ],
      ),
      body: _error != null
          ? _ErrorView(message: _error!, onRetry: _load)
          : Stack(
              children: [
                FlutterMap(
                  options: MapOptions(initialCenter: _center, initialZoom: 15),
                  children: [
                    TileLayer(
                      urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                      userAgentPackageName: 'co.edu.ecoruta',
                    ),
                    MarkerLayer(
                      markers: [
                        for (final h in _hotspots)
                          Marker(
                            point: LatLng(h.lat, h.lon),
                            width: 48,
                            height: 48,
                            child: _HotspotMarker(hotspot: h),
                          ),
                      ],
                    ),
                  ],
                ),
                if (_loading) const LinearProgressIndicator(),
                Positioned(
                  left: 16,
                  right: 16,
                  bottom: 16,
                  child: _Summary(count: _hotspots.length),
                ),
              ],
            ),
    );
  }
}

class _HotspotMarker extends StatelessWidget {
  const _HotspotMarker({required this.hotspot});

  final Hotspot hotspot;

  Color get _color => switch (hotspot.priority) {
        'Alta' => const Color(0xFFB3261E),
        'Media' => const Color(0xFFE65100),
        _ => const Color(0xFF2E7D5B),
      };

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message:
          '${hotspot.reportCount} reportes · ${hotspot.dominantCategory.label} · prioridad ${hotspot.priority}',
      child: Container(
        decoration: BoxDecoration(
          color: _color.withValues(alpha: 0.85),
          shape: BoxShape.circle,
          border: Border.all(color: Colors.white, width: 2),
        ),
        alignment: Alignment.center,
        child: Text(
          '${hotspot.reportCount}',
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}

class _Summary extends StatelessWidget {
  const _Summary({required this.count});

  final int count;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: const Icon(Icons.place_outlined),
        title: Text('$count puntos críticos en tu zona'),
        subtitle: const Text('Agrupados por cercanía y severidad acumulada'),
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.cloud_off, size: 48),
            const SizedBox(height: 12),
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 16),
            FilledButton(onPressed: onRetry, child: const Text('Reintentar')),
          ],
        ),
      ),
    );
  }
}
