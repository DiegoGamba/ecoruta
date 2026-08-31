# 6. Pruebas y resultados

## 6.1 Estrategia

La estrategia se apoya en una decisión de arquitectura: el dominio no conoce AWS. Gracias
a eso, la lógica de negocio se prueba contra un `InMemoryReportRepository` con la misma
semántica que el real, sin credenciales, sin red y sin costo.

| Nivel | Qué verifica | Dobles usados |
|---|---|---|
| Unitario de dominio | Geohash, distancia, agrupamiento, validaciones, transiciones | Ninguno (funciones puras) |
| Unitario de servicio | Casos de uso completos, indicadores, publicación de eventos | Repositorio en memoria, publicador nulo |
| Contrato HTTP | Códigos de estado, cabeceras, autorización por grupo, no filtración de datos | Evento de API Gateway construido a mano |
| Lógica de integración | Mapeo de etiquetas de Rekognition, reglas de alerta | Respuestas de servicio simuladas |

## 6.2 Resultados de la ejecución

```
$ pytest --cov=src
112 passed in 0.49s

Cobertura por módulo
  src/common/geo.py                 100 %
  src/common/services.py            100 %
  src/handlers/create_report.py     100 %
  src/handlers/get_report.py        100 %
  src/handlers/hotspots.py          100 %
  src/handlers/indicators.py        100 %
  src/common/http.py                 98 %
  src/common/models.py               98 %
  src/handlers/update_status.py      94 %
  ---------------------------------------
  TOTAL                              82 %
```

El 18 % no cubierto corresponde a código que solo se ejecuta contra AWS real: los
métodos de `DynamoReportRepository`, la composición de clientes en `deps.py`, la firma de
URLs y las llamadas a Rekognition y SNS. La lógica de decisión de esos módulos —el mapeo
de etiquetas, la regla de urgencia— sí está cubierta al haberse extraído a funciones puras.

### Verificación del geohash

La implementación propia se valida contra el vector de referencia estándar de la
especificación: `(57.64911, 10.40744) → u4pruydqq...`, además de propiedades esperadas
(estabilidad, prefijo compartido entre puntos cercanos, longitud según precisión).

### Un defecto encontrado por las pruebas

La prueba `test_no_expone_al_usuario` falló en su primera ejecución: `create` devolvía el
ítem completo de DynamoDB, incluyendo `user_id` y `ttl`, porque solo filtraba las claves
de índice. Se corrigió centralizando la proyección pública en `ReportService._public()`,
usada ahora por los tres métodos que devuelven un reporte. Es exactamente la clase de
fuga silenciosa de datos personales que motivó escribir esa prueba.

## 6.3 Comportamiento del agrupamiento

Escenario reproducible con la suite: cuatro reportes en un radio de 8 metros sobre la
Avenida El Dorado.

| Entrada | Resultado |
|---|---|
| 4 reportes, severidades 3, 3, 4, 5 | 1 punto crítico, severidad acumulada 15, prioridad **Alta** |
| Los mismos, tras marcarlos `atendido` | 0 puntos críticos (los cerrados salen del análisis) |
| 2 reportes cercanos únicamente | 0 puntos críticos (no alcanza el umbral de 3) |
| 3 cercanos + 3 a 4 km | 2 puntos críticos independientes |

El radio solicitado se acota en el servidor entre 30 y 1000 m: un cliente que pida
99.999 m recibe 1000, lo que impide convertir el endpoint en un escaneo de toda la ciudad.

## 6.4 Calidad estática

| Verificación | Estado |
|---|---|
| `ruff check` (E, F, I, B, UP, SIM, C4, ARG, RET) | Sin hallazgos |
| `bandit -r src/` | Sin hallazgos de severidad media o alta |
| `terraform fmt -check` | Formato conforme |
| `terraform validate` | Configuración válida |
| `flutter analyze` | Sin advertencias con `flutter_lints` |

## 6.5 Evidencias

La carpeta [`docs/evidencias/`](evidencias/) recoge las capturas de la solución
desplegada: salida de `terraform apply`, consola de las Lambdas, tabla de DynamoDB con
reportes reales, tablero de CloudWatch y la app en ejecución. El archivo
[`api.http`](../backend/api.http) contiene peticiones listas para reproducir el flujo
completo contra el despliegue propio.

## 6.6 Limitaciones de la validación actual

Ser explícito sobre el alcance de lo probado:

1. **Sin pruebas de carga.** No se ha medido el comportamiento bajo miles de reportes
   simultáneos ni el efecto de particiones calientes en un evento masivo.
2. **Sin validación de campo.** El agrupamiento se probó con datos sintéticos y con
   coordenadas reales de Bogotá, pero no contra un inventario oficial de puntos críticos.
   Esa comparación es el siguiente paso y la base de la propuesta de semillero.
3. **Precisión del clasificador no medida.** No existe todavía un conjunto etiquetado
   propio contra el cual calcular precisión y exhaustividad de Rekognition.
4. **Cobertura de la capa de integración.** El repositorio real se ejercita solo en el
   despliegue; faltan pruebas con un doble local de DynamoDB.

---

Anterior: [ADR](05-decisiones-adr.md) ·
Siguiente: [Proyección investigativa](07-proyeccion-investigativa.md)
