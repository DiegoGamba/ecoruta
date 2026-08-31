/// Configuración inyectada en tiempo de compilación.
///
/// Se usa `--dart-define` en vez de un archivo versionado para que ningún
/// identificador de entorno quede en el repositorio:
///
///   flutter run --dart-define=API_BASE_URL=... --dart-define=COGNITO_CLIENT_ID=...
class AppConfig {
  static const String apiBaseUrl = String.fromEnvironment('API_BASE_URL');
  static const String userPoolId = String.fromEnvironment('COGNITO_USER_POOL_ID');
  static const String clientId = String.fromEnvironment('COGNITO_CLIENT_ID');
  static const String region =
      String.fromEnvironment('AWS_REGION', defaultValue: 'us-east-1');

  static bool get isComplete =>
      apiBaseUrl.isNotEmpty && userPoolId.isNotEmpty && clientId.isNotEmpty;
}
