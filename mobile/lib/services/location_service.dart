import 'package:geolocator/geolocator.dart';

class LocationDeniedException implements Exception {
  LocationDeniedException(this.message);
  final String message;
}

/// Obtención de la ubicación con manejo explícito de permisos.
/// Se pide el permiso en el momento del reporte (no al abrir la app), que es
/// cuando el usuario entiende para qué se usa.
class LocationService {
  Future<Position> current() async {
    if (!await Geolocator.isLocationServiceEnabled()) {
      throw LocationDeniedException('Active la ubicación del dispositivo.');
    }

    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    if (permission == LocationPermission.denied ||
        permission == LocationPermission.deniedForever) {
      throw LocationDeniedException(
        'Se necesita la ubicación para georreferenciar el reporte.',
      );
    }

    return Geolocator.getCurrentPosition(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        timeLimit: Duration(seconds: 15),
      ),
    );
  }
}
