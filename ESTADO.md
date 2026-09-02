# Estado real del proyecto

Qué está construido y verificado, y qué no. Este archivo existe para que nadie —ni el
autor durante la sustentación— afirme más de lo que el repositorio respalda.

Última actualización: 2 de septiembre de 2026.

## Funciona y se puede demostrar hoy

| Componente | Estado | Cómo se comprueba |
|---|---|---|
| Lógica de dominio (geohash, agrupamiento, validación, transiciones, indicadores) | **Funciona** | `cd backend && pytest` → 112 pruebas, 82 % de cobertura |
| Los 8 handlers de las Lambdas | **Funcionan** | Se ejecutan en la demostración local y en las pruebas de contrato |
| API completa (crear, consultar, cambiar estado, puntos críticos, indicadores) | **Funciona** | `python3 demo/local_server.py` → `http://localhost:8000` |
| Integración continua | **Funciona** | [Actions → CI](https://github.com/DiegoGamba/ecoruta/actions/workflows/ci.yml), en verde |
| Documentación técnica y presentación | **Completas** | `docs/` y `presentacion/` |

## Escrito y verificado estáticamente, pero nunca ejecutado

| Componente | Estado | Qué falta |
|---|---|---|
| Infraestructura Terraform (43 recursos) | **Escrita y validada**, nunca aplicada | Una cuenta de AWS y `terraform apply` |
| Aplicación móvil Flutter | **Escrita**, pasa `flutter analyze` y sus pruebas | Generar las carpetas de plataforma, compilar e instalar en un dispositivo |
| Clasificación con Rekognition | **Escrita**, su lógica de mapeo está probada | Requiere el despliegue: nunca se ha llamado al servicio real |
| Alertas por SNS y eventos de EventBridge | **Escritos**, la regla de urgencia está probada | Requieren el despliegue |

"Validada" significa que `terraform validate` y `terraform fmt -check` pasan en el
pipeline. **No** significa que los recursos existan en AWS.

## Cómo enunciarlo en la sustentación

Correcto:

> "La lógica de negocio está implementada y probada, y se las voy a mostrar funcionando.
> La infraestructura está completa en Terraform y validada en el pipeline; el despliegue a
> una cuenta de AWS es el siguiente paso. La aplicación móvil está escrita y pasa el
> análisis estático, pero no la he compilado en un dispositivo."

Incorrecto:

> ~~"La solución está desplegada en AWS."~~
> ~~"La app móvil funciona en Android y iOS."~~

Un jurado penaliza mucho más una afirmación falsa detectada que un alcance incompleto
reconocido a tiempo.

## Lo que sigue, en orden de impacto

1. **Desplegar en AWS** (`docs/08-despliegue.md`). Cabe en la capa gratuita. Convierte
   toda la segunda tabla de este archivo en la primera.
2. **Compilar la app móvil**: `cd mobile && flutter create --project-name ecoruta --org co.edu.ecoruta .` y luego `flutter run`.
3. **Capturar las evidencias** que quedan listadas en `docs/evidencias/README.md`.
