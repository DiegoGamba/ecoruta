# 1. Análisis del problema

## 1.1 Situación problema

En las ciudades colombianas, una fracción significativa de los residuos sólidos no
llega al sistema formal de recolección, sino que se acumula en **puntos críticos**:
esquinas, separadores, orillas de quebrada y lotes baldíos donde se dispone basura
fuera de horario y fuera de ruta. El fenómeno tiene tres características que lo hacen
difícil de atender con los instrumentos actuales:

1. **Es dinámico.** Un punto crítico aparece, se erradica y reaparece a media cuadra.
   Los inventarios estáticos que levantan las entidades quedan desactualizados en semanas.
2. **Es local.** Quien mejor lo detecta —de forma inmediata y precisa— es el vecino que
   pasa por ahí todos los días, no el operador que recorre la macro-ruta.
3. **La información no fluye.** Los canales de reporte disponibles (línea telefónica,
   formulario web, redes sociales) producen texto libre sin coordenadas ni evidencia,
   lo que obliga a una verificación en campo antes de programar cualquier intervención.

El resultado operativo es un ciclo largo entre que el residuo aparece y que la cuadrilla
llega, con costos evitables: recolección reactiva y no optimizada, riesgo sanitario por
vectores, obstrucción de sumideros y deterioro del espacio público.

## 1.2 Delimitación

| Dimensión | Alcance de esta entrega |
|---|---|
| Actor primario | Ciudadano residente de la zona urbana |
| Actor secundario | Operador / supervisor de la entidad de aseo |
| Territorio piloto | Una localidad urbana (validación con datos de Bogotá) |
| Flujo cubierto | Reporte georreferenciado → clasificación → agrupamiento → priorización → cierre |
| Fuera de alcance | Facturación del servicio, despacho de vehículos, comparendo ambiental |

## 1.3 Pregunta problema

> **¿De qué manera el diseño de una aplicación móvil multiplataforma en Flutter, con
> captura georreferenciada y sincronización *offline-first*, permite reducir a menos de
> 60 segundos el tiempo de reporte de un punto crítico de residuos sólidos y sostener una
> tasa de envío exitoso superior al 95 % en zonas con conectividad intermitente?**

La pregunta es de ingeniería de software móvil y es medible: sus dos variables —tiempo de
registro y tasa de envío— se instrumentan en la propia aplicación.

De ella se desprende una pregunta de alcance investigativo, que orienta la continuidad del
trabajo en el semillero y se desarrolla en el [documento 7](07-proyeccion-investigativa.md):

> ¿Puede el inventario de puntos críticos derivado de reportes ciudadanos resultar más
> actualizado y accionable que el levantamiento manual periódico?

## 1.4 Objetivos

### Objetivo general (SMART)

> **Desarrollar** una aplicación móvil multiplataforma en **Flutter** con sincronización
> *offline-first*, que permita a un ciudadano registrar un punto crítico de residuos
> sólidos —georreferenciado y con evidencia fotográfica— en **menos de 60 segundos**,
> sosteniendo una **tasa de envío exitoso superior al 95 %** en zonas con conectividad
> intermitente, **antes del 10 de septiembre de 2026**.

| Criterio | Cómo lo cumple |
|---|---|
| **E**specífico | Una app Flutter para un flujo concreto: capturar y enviar un reporte georreferenciado |
| **M**edible | Dos métricas instrumentables: tiempo de registro (< 60 s) y tasa de envío (> 95 %) |
| **A**lcanzable | La cola local en el dispositivo hace viable la tasa de envío sin conectividad continua |
| **R**elevante | Ataca la causa por la que el reporte ciudadano no fluye hoy: fricción y falta de señal |
| **T**emporal | Fecha límite del taller: 10 de septiembre de 2026 |

### Objetivos específicos

Siguen los tres pasos del ciclo de vida móvil.

**Paso 1 · Investigación de usuario y prototipado UX/UI.**
Diseñar el flujo de captura y las tres pantallas de la aplicación (reporte, mapa de puntos
críticos y navegación), evaluando las heurísticas de usabilidad de Nielsen y verificando
contraste accesible AA y objetivos táctiles de al menos 48 dp, en la **semana 3**.

**Paso 2 · Desarrollo del frontend móvil e integración con el backend.**
Programar los módulos del cliente en Flutter —captura con cámara y GPS, cola local de
envíos y mapa— e integrar el consumo de la API REST desplegada sobre AWS con
autenticación por Cognito, en la **semana 6**.

**Paso 3 · Pruebas en dispositivos reales y medición de rendimiento.**
Medir en dispositivos Android e iOS el tiempo de registro de un reporte, la tasa de envío
exitoso en modo avión y con red intermitente, el consumo de batería durante una sesión de
captura y la usabilidad percibida mediante el cuestionario SUS, en la **semana 8**.

## 1.4.1 Metodología de desarrollo

**Scrum adaptado al ciclo de vida móvil**, con sprints de dos semanas. Se eligió por dos
razones: el alcance se descubre a medida que se prueba con usuarios reales, y cada sprint
debe cerrar con un incremento instalable en un dispositivo, no con un documento.

Cada sprint recorre las cuatro actividades del ciclo móvil:

| Actividad | Qué produce | Artefacto en este repositorio |
|---|---|---|
| **Diseño UX/UI** | Flujo de pantallas, sistema visual accesible | `mobile/lib/theme.dart`, `mobile/lib/screens/` |
| **Prototipado** | Pantallas navegables sobre datos de prueba | Demostración local (`demo/`) |
| **Sprint de código** | Incremento probado y en integración continua | Commits + `.github/workflows/ci.yml` |
| **Pruebas en dispositivos** | Métricas de tiempo, batería y usabilidad | Pendiente: es el objetivo específico 3 |

Se consideró **Mobile-D**, que es una metodología específica para desarrollo móvil, pero su
estructura de cinco fases resulta pesada para un equipo de una persona y un horizonte de
ocho semanas. Scrum adaptado conserva la cadencia corta sin la carga ceremonial.

## 1.5 Justificación de la propuesta tecnológica

La decisión central es una arquitectura **serverless en AWS**. La justificación no es
de moda tecnológica sino de correspondencia con el perfil del problema:

| Característica del problema | Consecuencia técnica | Servicio elegido |
|---|---|---|
| Demanda muy irregular (picos tras jornadas de limpieza o lluvias; casi nula de madrugada) | Se necesita escalar a cero y absorber picos sin aprovisionar servidores | Lambda + API Gateway HTTP API |
| Un proyecto piloto universitario sin presupuesto de operación | El costo debe ser proporcional al uso real, no al tiempo encendido | Facturación por invocación; DynamoDB `PAY_PER_REQUEST` |
| Consultas siempre por zona geográfica o por estado | El acceso es por clave conocida, no analítico ni relacional | DynamoDB single-table con GSI por geohash y por estado |
| Evidencia fotográfica pesada respecto al resto del payload | La imagen no debe atravesar la capa de cómputo | S3 con URL prefirmada, subida directa desde el dispositivo |
| Clasificar residuo desde una foto sin dataset propio inicial | Se requiere una línea base inmediata, reemplazable después | Rekognition `DetectLabels` como baseline |
| Nuevos consumidores del evento "reporte creado" a futuro | El productor no debe conocer a sus consumidores | EventBridge (publicación/suscripción) |
| Datos personales implícitos (ubicación, foto) | Cifrado, mínimo privilegio y retención acotada son obligatorios | KMS, IAM por función, TTL de 540 días |

### Alternativas consideradas y descartadas

- **Contenedores sobre ECS/EKS.** Rechazado: el costo base de mantener tareas activas no
  se justifica con el patrón de tráfico, y la carga operativa (parcheo, escalado, red)
  supera lo razonable para el alcance.
- **PostgreSQL + PostGIS.** Técnicamente superior para consultas geoespaciales complejas,
  pero introduce una instancia siempre encendida y una VPC que la solución no necesita:
  las consultas reales son "reportes cerca de este punto", que el prefijo de geohash
  resuelve con un `Query` de costo constante.
- **Firebase.** Menor fricción inicial, pero el proyecto persigue explícitamente el
  ejercicio de arquitectura en la nube con infraestructura como código, control de IAM
  fino y trazabilidad — más transferible al perfil profesional buscado.

## 1.6 Fuentes y contexto

El planteamiento se apoya en la existencia de programas municipales de erradicación de
puntos críticos y de inventarios publicados como datos abiertos por las entidades de
aseo, que evidencian tanto la relevancia del fenómeno como el vacío de actualización
continua que esta solución aborda.

---

Siguiente: [Arquitectura de la solución](02-arquitectura.md)
