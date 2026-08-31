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

## 1.3 Pregunta que guía el proyecto

> ¿Puede un flujo de reporte ciudadano georreferenciado, con evidencia fotográfica y
> agrupamiento espacial automático, producir un inventario de puntos críticos más
> actualizado y accionable que el levantamiento manual periódico?

## 1.4 Objetivos

**General.** Diseñar e implementar una solución móvil respaldada por una arquitectura
en la nube que capture, clasifique y priorice puntos críticos de residuos sólidos a
partir del reporte ciudadano.

**Específicos**

1. Capturar un reporte georreferenciado con evidencia fotográfica en menos de 60 segundos,
   incluso sin conectividad en el momento de la captura.
2. Convertir reportes individuales dispersos en **puntos críticos** mediante agrupamiento
   espacial, y priorizarlos por severidad acumulada.
3. Sugerir automáticamente el tipo de residuo a partir de la fotografía, para reducir la
   carga de clasificación sobre el ciudadano y estandarizar el dato.
4. Notificar de inmediato al operador cuando el reporte involucre residuos peligrosos o
   severidad alta.
5. Exponer indicadores operativos (volumen, tasa de atención, pendientes) para el
   seguimiento de la entidad.

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
