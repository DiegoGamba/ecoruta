import 'package:flutter/material.dart';

import 'app_config.dart';
import 'screens/home_shell.dart';
import 'services/api_client.dart';
import 'services/auth_service.dart';
import 'services/location_service.dart';
import 'services/offline_queue.dart';
import 'theme.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const EcoRutaApp());
}

class EcoRutaApp extends StatefulWidget {
  const EcoRutaApp({super.key});

  @override
  State<EcoRutaApp> createState() => _EcoRutaAppState();
}

class _EcoRutaAppState extends State<EcoRutaApp> {
  late final AuthService _auth = AuthService();
  late final ApiClient _api = ApiClient(baseUrl: AppConfig.apiBaseUrl, auth: _auth);
  late final LocationService _location = LocationService();
  late final OfflineQueue _queue = OfflineQueue(_api);

  late final Future<void> _bootstrap = _init();

  Future<void> _init() async {
    if (!AppConfig.isComplete) {
      throw StateError(
        'Faltan variables de compilación. Ejecute con --dart-define '
        '(vea el README, sección "Ejecutar la app").',
      );
    }
    await _auth.configure(AppConfig.userPoolId, AppConfig.clientId, AppConfig.region);
  }

  @override
  void dispose() {
    _api.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'EcoRuta',
      debugShowCheckedModeBanner: false,
      theme: EcoTheme.light(),
      darkTheme: EcoTheme.dark(),
      home: FutureBuilder<void>(
        future: _bootstrap,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Scaffold(body: Center(child: CircularProgressIndicator()));
          }
          if (snapshot.hasError) {
            return Scaffold(
              body: Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Text('${snapshot.error}', textAlign: TextAlign.center),
                ),
              ),
            );
          }
          return HomeShell(
            api: _api,
            auth: _auth,
            location: _location,
            queue: _queue,
          );
        },
      ),
    );
  }
}
