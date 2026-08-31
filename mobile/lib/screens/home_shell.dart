import 'package:flutter/material.dart';

import '../services/api_client.dart';
import '../services/location_service.dart';
import '../services/offline_queue.dart';
import 'map_screen.dart';
import 'report_form_screen.dart';

/// Contenedor con navegación inferior. Al abrir, intenta vaciar la cola de
/// reportes pendientes que quedaron sin enviar por falta de conexión.
class HomeShell extends StatefulWidget {
  const HomeShell({
    super.key,
    required this.api,
    required this.location,
    required this.queue,
  });

  final ApiClient api;
  final LocationService location;
  final OfflineQueue queue;

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _index = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _flushQueue());
  }

  Future<void> _flushQueue() async {
    final sent = await widget.queue.flush();
    if (sent > 0 && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Se sincronizaron $sent reportes pendientes.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final screens = [
      ReportFormScreen(api: widget.api, location: widget.location, queue: widget.queue),
      MapScreen(api: widget.api, location: widget.location),
    ];

    return Scaffold(
      body: IndexedStack(index: _index, children: screens),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.add_circle_outline),
            selectedIcon: Icon(Icons.add_circle),
            label: 'Reportar',
          ),
          NavigationDestination(
            icon: Icon(Icons.map_outlined),
            selectedIcon: Icon(Icons.map),
            label: 'Mapa',
          ),
        ],
      ),
    );
  }
}
