# Evidencias

## Disponibles

Estas evidencias se generaron ejecutando el proyecto y están versionadas aquí.

| Archivo | Qué muestra |
|---|---|
| `01-demo-panel-inicial.png` | La demostración local recién arrancada: 37 reportes sembrados y **5 puntos críticos** detectados por el algoritmo de agrupamiento, priorizados por severidad acumulada |
| `02-demo-punto-nuevo.png` | Tras enviar tres reportes en el mismo lugar: aparece un **sexto punto crítico** y los indicadores pasan de 37 a 40 reportes. Es el umbral de tres reportes funcionando |
| `03-pruebas-backend.txt` | Salida de `pytest --cov=src`: 112 pruebas en verde, 82 % de cobertura |

Las dos capturas se tomaron sobre la [demostración local](../../demo/README.md), que
ejecuta los handlers reales de las Lambdas contra el repositorio en memoria. El mapa base
aparece liso porque el entorno donde se capturaron no tenía acceso a los mosaicos de
OpenStreetMap; en un equipo con internet el mapa se ve completo.

El estado del pipeline de integración continua se consulta en vivo:
[Actions → CI](https://github.com/DiegoGamba/ecoruta/actions/workflows/ci.yml).

## Pendientes: despliegue en AWS

Estas evidencias requieren una cuenta de AWS y se agregan tras ejecutar
`terraform apply` siguiendo [`docs/08-despliegue.md`](../08-despliegue.md).

| Archivo sugerido | Qué debe mostrar |
|---|---|
| `10-terraform-apply.png` | Salida de `terraform apply` con los recursos creados |
| `11-lambdas.png` | Consola de AWS con las 8 funciones desplegadas |
| `12-api-gateway.png` | Rutas del API con el autorizador JWT asociado |
| `13-dynamodb.png` | Tabla con reportes reales y los tres índices |
| `14-s3-evidencias.png` | Bucket con las fotografías y el bloqueo de acceso público activo |
| `15-cloudwatch.png` | Tablero operativo y alarmas |
| `16-app-reporte.png` | Pantalla de reporte en el dispositivo |
| `17-app-mapa.png` | Mapa con puntos críticos en la app móvil |
| `18-alerta-sns.png` | Correo de alerta por residuo peligroso |

Mientras tanto, la lógica que esos recursos ejecutarían está verificada por las 112
pruebas y demostrable con la demostración local.
