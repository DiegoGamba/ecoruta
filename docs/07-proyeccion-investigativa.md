# 7. Proyección investigativa (Semillero)

Este documento plantea cómo el proyecto pasa de ser un desarrollo de curso a una línea
de investigación con resultados publicables.

## 7.1 Vacío identificado

La gestión de puntos críticos de residuos sólidos en ciudades colombianas se apoya en
inventarios levantados manualmente y actualizados con baja periodicidad. Existe
literatura sobre *crowdsourcing* ambiental y sobre clasificación automática de residuos
(TrashNet, TACO), pero es escasa la evidencia sobre **la combinación de ambos en
contextos urbanos latinoamericanos**, y en particular sobre una pregunta operativa
concreta: ¿el reporte ciudadano agrupado espacialmente reproduce, anticipa o complementa
el inventario oficial?

## 7.2 Preguntas de investigación

**P1.** ¿Con qué precisión y exhaustividad los puntos críticos derivados de reportes
ciudadanos coinciden con el inventario oficial de la entidad de aseo?

**P2.** ¿Qué configuración de parámetros de agrupamiento (radio ε, mínimo de reportes,
ventana temporal) maximiza la concordancia con el inventario oficial?

**P3.** ¿Un clasificador propio, entrenado con imágenes del contexto local, supera a un
servicio genérico de visión por computador en la categorización de residuos de vía
pública, y con qué costo de inferencia?

**P4.** ¿Existen patrones espacio-temporales recurrentes (día de la semana, proximidad a
plazas de mercado, obras o cuerpos de agua) que permitan **anticipar** la aparición de un
punto crítico antes de que sea reportado?

## 7.3 Diseño metodológico propuesto

### Fase 1 — Validación concurrente (P1, P2)

- **Datos.** Reportes recogidos por la app durante un piloto de 12 semanas en una
  localidad, contrastados con el inventario oficial publicado como dato abierto.
- **Método.** Emparejamiento espacial por distancia entre centroides con umbral variable;
  cálculo de precisión, exhaustividad y F1 tratando el inventario oficial como referencia.
- **Análisis de sensibilidad.** Barrido de ε ∈ {50, 80, 120, 200, 300} m y mínimo de
  reportes ∈ {2, 3, 5}, reportando la superficie de F1 para justificar los valores por
  defecto que hoy están fijados por criterio.
- **Producto.** Curva de concordancia y una recomendación de parámetros basada en
  evidencia, no en intuición.

### Fase 2 — Clasificador propio (P3)

- **Corpus.** Las evidencias acumuladas por el piloto, anonimizadas (desenfoque de rostros
  y placas) y etiquetadas con doble anotador más resolución de desacuerdos (κ de Cohen).
- **Modelos.** Línea base Rekognition frente a un MobileNetV3 o EfficientNet-Lite ajustado
  por transferencia, evaluado con validación cruzada estratificada.
- **Métricas.** F1 macro por categoría, matriz de confusión, latencia y costo por 1000
  inferencias; se contempla ejecución **en el dispositivo** (TensorFlow Lite) para
  clasificar sin conexión y sin costo por llamada.
- **Producto.** Comparación cuantitativa y, si el resultado lo respalda, un conjunto de
  datos abierto de residuos urbanos colombianos — un aporte reutilizable por sí mismo.

### Fase 3 — Modelo predictivo (P4)

- **Variables.** Historial de reportes, día y hora, proximidad a puntos de interés
  (plazas de mercado, obras, cuerpos de agua), precipitación, frecuencia de recolección.
- **Método.** Agregación en rejilla de geohash 7 y modelo de conteo (regresión de Poisson
  o gradient boosting) para estimar la probabilidad de reaparición a 7 días; evaluación
  con partición temporal, nunca aleatoria, para no filtrar el futuro.
- **Producto.** Mapa de riesgo que permita pasar de recolección reactiva a preventiva.

## 7.4 Qué habilita ya la arquitectura actual

La proyección no es una lista de deseos: el diseño actual la sostiene.

| Necesidad de la investigación | Elemento ya implementado |
|---|---|
| Corpus etiquetado de imágenes | Evidencias en S3 con ciclo de vida y `ai_labels` almacenadas |
| Línea base contra la cual comparar | Rekognition con mapeo explícito y umbral documentado |
| Serie espacio-temporal | `geohash` + `created_at` indexados en GSI1 |
| Reproducibilidad de los parámetros | Radio y umbral configurables por variable de entorno y por query |
| Nuevos consumidores de datos sin tocar el código | Publicación en EventBridge |
| Trazabilidad de cada decisión automática | Logs estructurados en JSON con la categoría sugerida |

## 7.5 Resultados esperados y difusión

1. Artículo corto con la validación concurrente (P1–P2) para un congreso nacional de
   ingeniería de sistemas o de ingeniería ambiental.
2. Conjunto de datos abierto de residuos urbanos con licencia permisiva.
3. Prototipo del clasificador en el dispositivo, medible en precisión, latencia y costo.
4. Repositorio público con código, infraestructura como código y documentación, de modo
   que los resultados sean reproducibles por terceros.

## 7.6 Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Volumen de reportes insuficiente para el piloto | Alianza con juntas de acción comunal y con la asignatura como fuente inicial de usuarios |
| Sesgo de participación (más reportes donde hay más smartphones) | Reportarlo explícitamente como limitación; ponderar por densidad poblacional |
| Inventario oficial desactualizado como referencia | Tratar la discordancia como hallazgo, no como error: un punto reportado y ausente del inventario es precisamente la hipótesis del proyecto |
| Datos personales en las fotografías | Anonimización obligatoria antes de cualquier uso del corpus |

---

Anterior: [Pruebas y resultados](06-pruebas-resultados.md) ·
Siguiente: [Guía de despliegue](08-despliegue.md)
