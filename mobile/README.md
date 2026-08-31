# App móvil EcoRuta

Flutter 3.22 · Android e iOS.

## Generar las carpetas de plataforma

El repositorio versiona únicamente el código fuente (`lib/`, `test/`, `pubspec.yaml`).
Las carpetas `android/`, `ios/` y `web/` son artefactos generados: se recrean con

```bash
cd mobile
flutter create --project-name ecoruta --org co.edu.ecoruta .
flutter pub get
```

## Ejecutar

La configuración se inyecta en tiempo de compilación, para que ningún identificador de
entorno quede versionado:

```bash
flutter run \
  --dart-define=API_BASE_URL=https://xxxx.execute-api.us-east-1.amazonaws.com/dev \
  --dart-define=COGNITO_USER_POOL_ID=us-east-1_xxxxxxxx \
  --dart-define=COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx \
  --dart-define=AWS_REGION=us-east-1
```

Los valores los produce Terraform: `terraform output mobile_env`.

## Permisos requeridos

| Plataforma | Permiso | Motivo |
|---|---|---|
| Android | `ACCESS_FINE_LOCATION`, `CAMERA`, `INTERNET` | Georreferenciar el reporte y capturar la evidencia |
| iOS | `NSLocationWhenInUseUsageDescription`, `NSCameraUsageDescription` | Ídem |

El permiso de ubicación se solicita en el momento de enviar el reporte, no al abrir la
app: es cuando el usuario entiende para qué se usa.

## Estructura

```
lib/
├── main.dart              Arranque y composición de dependencias
├── app_config.dart        Configuración por --dart-define
├── theme.dart             Sistema visual Material 3 accesible
├── models/report.dart     Modelos de dominio (Report, Hotspot, enums)
├── services/
│   ├── api_client.dart      Cliente HTTP con token de Cognito
│   ├── auth_service.dart    Autenticación (Amplify + Cognito)
│   ├── location_service.dart Ubicación con manejo de permisos
│   └── offline_queue.dart   Cola local de reportes sin conexión
└── screens/
    ├── home_shell.dart      Navegación inferior
    ├── report_form_screen.dart Formulario de reporte
    └── map_screen.dart      Mapa de puntos críticos
```

## Pruebas

```bash
flutter analyze
flutter test
```
