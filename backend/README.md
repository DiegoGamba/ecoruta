# Backend EcoRuta

API en Python 3.12 sobre AWS Lambda. Ocho funciones, una por caso de uso.

## Estructura

```
src/
├── handlers/     Adaptadores: traducen eventos HTTP/S3/EventBridge a casos de uso
│   ├── create_report.py      POST /reportes
│   ├── get_report.py         GET  /reportes/{id}
│   ├── update_status.py      PATCH /reportes/{id}/estado   (grupo: operadores)
│   ├── hotspots.py           GET  /puntos-criticos
│   ├── indicators.py         GET  /indicadores             (grupo: operadores)
│   ├── presign_evidence.py   POST /evidencias/url
│   ├── classify_evidence.py  Evento de S3 → Rekognition
│   ├── notify_operator.py    Evento de EventBridge → SNS
│   └── deps.py               Composición de dependencias (clientes de AWS)
└── common/
    ├── models.py       Dominio y validación de entrada
    ├── geo.py          Geohash, Haversine y agrupamiento
    ├── services.py     Casos de uso (no conoce HTTP ni AWS)
    ├── repository.py   Acceso a datos: implementación DynamoDB y doble en memoria
    ├── http.py         Adaptadores de API Gateway y manejo de errores
    ├── config.py       Configuración por variables de entorno
    └── logging_utils.py Logs JSON con seudonimización
```

Las dependencias apuntan siempre hacia el dominio. Por eso las pruebas corren sin
credenciales de AWS y sin red.

## Desarrollo

```bash
pip install -r requirements-dev.txt
pytest --cov=src      # 109 pruebas
ruff check .
bandit -r src/ -ll
```

## Empaquetado

No hay paso manual: Terraform comprime `src/` con el proveedor `archive` y usa
`source_code_hash` para redesplegar solo cuando el código cambia. La única dependencia
externa es `boto3`, que el runtime de Lambda ya incluye.

## Probar contra un despliegue

Ver [`api.http`](api.http): el flujo completo listo para ejecutar desde VS Code o IntelliJ.
