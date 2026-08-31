# 10. Guion de sustentación

Material de apoyo para exponer el proyecto. Las mismas notas están incrustadas en el
`.pptx` como notas del expositor.

**Duración objetivo: 12 minutos** de exposición + preguntas. Si le dan 8, salte las
diapositivas 6, 7 y 11 (marcadas como *recortables*). Si le dan 20, profundice en 8 y 12.

---

## Antes de empezar

- Abra **dos pestañas**: el repositorio en GitHub y la consola de AWS con el tablero de
  CloudWatch. Que el evaluador vea que existe, no solo que se cuenta.
- Tenga el celular con la app lista para reportar. Una demostración de 30 segundos vale
  más que tres diapositivas.
- Si algo falla en vivo, no improvise arreglos: pase a la captura en `docs/evidencias/` y
  siga. Nunca depure código delante del jurado.

---

## Diapositiva 1 · Portada · 20 s

> "Buenos días. Voy a presentar EcoRuta, una solución móvil respaldada por una
> arquitectura serverless en AWS para el reporte ciudadano y la priorización automática
> de puntos críticos de residuos sólidos."

No lea la diapositiva. Diga el nombre, la frase de una línea, y avance.

---

## Diapositiva 2 · El problema · 90 s

Este es el minuto que decide si el jurado se interesa. **Cuente un caso concreto antes de
generalizar:**

> "Todos conocemos una esquina del barrio donde aparece basura. La recogen, y a la semana
> vuelve a aparecer media cuadra más allá."

Luego los tres rasgos, sin leerlos textualmente:

1. **Es dinámico** — el inventario que levanta la entidad queda obsoleto en semanas.
2. **Es local** — quien mejor lo detecta es el vecino, no el operador de la macro-ruta.
3. **La información no fluye** — los canales actuales dan texto libre sin coordenadas ni
   evidencia, así que toca ir a verificar en campo antes de mandar una cuadrilla.

Cierre con la consecuencia: *recolección reactiva, riesgo sanitario, sumideros tapados.*

---

## Diapositiva 3 · Pregunta y objetivos · 60 s

Lea **la pregunta de investigación en voz alta y completa**. Es lo que convierte el
trabajo en algo evaluable, y es lo que un jurado de semillero está esperando oír.

De los cinco objetivos mencione solo dos o tres; el resto está en pantalla. Priorice el
1 (60 segundos, incluso sin conectividad) y el 2 (convertir reportes dispersos en puntos
críticos priorizados), porque son los que sustentan la demostración.

---

## Diapositiva 4 · La solución · 60 s

Recorra los cinco pasos de izquierda a derecha, una frase cada uno. **Aquí es donde va la
demostración en vivo**: saque el celular, tome una foto, envíe el reporte, y muestre en
el mapa cómo aparece agrupado.

> "Lo que acaban de ver son treinta segundos. Ese es el objetivo de diseño: si reportar
> cuesta más que ignorar el problema, nadie reporta."

---

## Diapositiva 5 · Arquitectura · 2 min

Es la diapositiva más importante para la nota. **No enumere servicios: explique
decisiones.** Suba por las capas y en cada una diga *por qué*, no *qué*:

- **Borde.** "La validación del token la hace API Gateway, no mi código. Una petición sin
  credenciales válidas nunca llega a ejecutar una función mía."
- **Cómputo.** "Ocho funciones, una por caso de uso. Eso me permite mínimo privilegio
  real: la función que consulta un reporte solo puede leer; la que firma la subida de
  fotos ni siquiera toca la base de datos."
- **Datos.** "Una sola tabla, y ninguna operación usa `Scan`."
- **La flecha gruesa.** "La foto no atraviesa mi capa de cómputo: la app pide una URL
  prefirmada y sube directo a S3. Eso evita el límite de 6 MB de Lambda y ahorra
  transferir la imagen dos veces."

---

## Diapositiva 6 · Justificación tecnológica · 90 s · *recortable*

No lea las seis filas. Elija **dos** y explíquelas bien; luego mencione lo descartado,
que es lo que demuestra criterio:

> "Consideré PostgreSQL con PostGIS, que es técnicamente superior para consultas
> espaciales complejas. Lo descarté porque mis consultas reales son 'qué hay cerca de
> este punto', que un prefijo de geohash resuelve a costo constante, y PostGIS me
> obligaba a una instancia siempre encendida dentro de una VPC —que por sí sola cuesta
> más que toda la solución."

---

## Diapositiva 7 · Modelo de datos · 90 s · *recortable*

La frase que resume todo:

> "En DynamoDB uno no diseña desde las entidades, sino desde las consultas. Tengo
> exactamente cuatro consultas y cada una tiene su clave."

Si hay tiempo, explique el geohash a dos precisiones: se guarda con precisión 7 pero se
particiona por 6. Es una decisión con un razonamiento concreto detrás —particiones ni
diminutas ni calientes— y es el tipo de detalle que distingue una arquitectura pensada de
una copiada.

---

## Diapositiva 8 · Algoritmo · 2 min

**Aquí es donde se gana el criterio de rigor técnico.** Es lo único verdaderamente propio
del proyecto, así que dedíquele tiempo.

Explique los cuatro pasos y sea explícito con el umbral:

> "Un grupo solo se considera punto crítico con tres o más reportes. Sin ese umbral, una
> queja aislada movilizaría una cuadrilla."

Y señale el panel de la derecha:

> "Estos casos no son ilustrativos: son pruebas automatizadas que corren en cada push.
> Incluida la última, que verifica que si alguien pide un radio de 99 kilómetros el
> servidor lo acota a uno, para que el endpoint no se convierta en un escaneo de la
> ciudad entera."

---

## Diapositiva 9 · Seguridad · 90 s

Elija **dos tarjetas**, no las seis. Recomendadas: *mínimo privilegio real* y
*seudonimización en logs*.

Luego —y esto importa más de lo que parece— **lea la deuda reconocida**:

> "Quiero ser explícito con lo que falta: no verifico que la foto se haya tomado donde
> dice, no hay WAF, y no desenfoco rostros. Lo documenté porque un análisis de seguridad
> que solo lista lo que sí hice no es un análisis de seguridad."

Un jurado premia esa honestidad; y si no lo dice usted, se lo van a preguntar igual.

---

## Diapositiva 10 · Calidad · 60 s

Los cuatro números, y **una historia concreta** que vale más que todos ellos:

> "Una de las pruebas falló la primera vez que la corrí. La API estaba devolviendo el
> identificador del usuario junto con el reporte. Es una fuga de datos personales que no
> se ve mirando el código, solo se ve cuando alguien la prueba. Está documentada en el
> informe de resultados."

---

## Diapositiva 11 · Costos · 60 s · *recortable*

> "El piloto completo cuesta menos de cinco dólares al mes, y la demostración que acaban
> de ver cabe en la capa gratuita de AWS. Pero el dato interesante es la composición: el
> 62 % es el servicio de visión por computador. Eso no es un problema de presupuesto, es
> el argumento de la siguiente diapositiva."

Ese puente hacia la investigación es el mejor momento de toda la presentación. Úselo.

---

## Diapositiva 12 · Semillero · 2 min

Si le interesa la convocatoria, **esta es la diapositiva por la que vino**.

- Nombre el vacío: hay literatura sobre reporte ciudadano y sobre clasificación de
  residuos, pero poca sobre las dos cosas juntas en ciudades latinoamericanas.
- Explique la Fase 1 con concreción: comparar los puntos críticos que produce la app
  contra el inventario oficial publicado como dato abierto, y medir precisión y
  exhaustividad. **Es un experimento ejecutable, no una intención.**
- Cierre con los habilitadores: "no es una lista de deseos; la arquitectura ya está
  acumulando el corpus y la serie espacio-temporal que esa investigación necesita."

---

## Diapositiva 13 · Entregables · 30 s

Muestre el repositorio en vivo, no la diapositiva. Baje por el README, abra un ADR, abra
la carpeta de evidencias. Diez segundos de repositorio real valen más que un minuto
describiéndolo.

---

## Diapositiva 14 · Cierre · 30 s

> "En resumen: el conocimiento local del vecino, convertido en un inventario vivo y
> priorizado. Problema delimitado, arquitectura justificada con sus alternativas
> descartadas por escrito, ingeniería verificable, y un camino de investigación abierto.
> Quedo atento a sus preguntas."

**No termine con "eso es todo".** Termine invitando a preguntar.

---

# Banco de preguntas

## Sobre la arquitectura

**¿Por qué serverless y no un servidor tradicional?**
Por el patrón de tráfico. Los reportes se concentran en picos —después de una jornada
comunitaria, después de una lluvia— y de madrugada no hay ninguno. Un servidor encendido
las 24 horas paga por el tiempo, no por el uso. Con Lambda pago por invocación y escalo a
cero. Además me ahorro parcheo de sistema operativo y gestión de red.

**¿Y el arranque en frío?**
Existe: entre 200 y 400 milisegundos en la primera invocación tras un rato de
inactividad. Para reportar basura no es un problema perceptible. Si lo fuera, hay
concurrencia aprovisionada, pero eso reintroduce costo fijo y no se justifica aquí.

**¿No es esto quedar atrapado en AWS?**
Parcialmente, y es una decisión consciente, documentada en el ADR-001. Lo mitigué con la
arquitectura: la lógica de negocio está en una capa que no conoce AWS ni HTTP. Migrar
significaría reescribir los adaptadores, no el dominio. La prueba de que esa separación
es real es que las 112 pruebas corren sin credenciales de AWS.

**¿Por qué ocho funciones y no una sola?**
Por permisos. Con un monolito, el rol de la función tendría que unir todos los permisos
de todos los endpoints. Con una función por caso de uso, la que consulta un reporte solo
puede leer. Como beneficio adicional, los fallos quedan aislados y tengo métricas por
endpoint sin instrumentar nada.

## Sobre los datos

**¿Por qué DynamoDB y no una base relacional?**
Porque mis consultas son de acceso por clave conocida, no analíticas ni relacionales:
"reportes cerca de este punto" y "reportes en este estado". DynamoDB las resuelve a costo
y latencia constantes. Si el proyecto necesitara consultas espaciales complejas
—intersecciones con polígonos de localidad, por ejemplo— PostGIS sería mejor, y lo dejé
escrito en el ADR-002.

**¿Cómo funciona la búsqueda geográfica sin PostGIS?**
Con geohash. Es una codificación que convierte una coordenada en una cadena donde puntos
cercanos comparten prefijo. Uso ese prefijo como clave de partición, así que traer el
vecindario es una sola consulta. Luego, dentro de ese conjunto pequeño, calculo distancias
reales con Haversine.

**¿Qué pasa si un barrio genera muchísimos reportes?**
Es el riesgo de partición caliente y por eso la partición es de ~1,2 km y no de 150 m.
No lo he medido bajo carga: lo declaro como limitación en el informe de resultados.

## Sobre el algoritmo

**¿Por qué DBSCAN y no k-means?**
Porque k-means exige decidir de antemano cuántos grupos hay, y yo no sé cuántos puntos
críticos tiene una localidad —justamente eso es lo que quiero descubrir. DBSCAN agrupa
por densidad: los grupos emergen de los datos, y los puntos aislados simplemente no
forman grupo.

**¿De dónde salen los 120 metros y los 3 reportes?**
De criterio, no de evidencia: 120 metros es aproximadamente una manzana urbana, y 3 es el
mínimo para que no sea una queja aislada. Reconozco que están fijados por juicio, y
validarlos empíricamente con un barrido de parámetros contra el inventario oficial es
exactamente la Fase 1 de la propuesta de semillero.

**¿Cómo evitan reportes falsos o duplicados?**
Los duplicados no son un problema: al contrario, tres personas reportando el mismo punto
es la señal que busco. Contra el fraude tengo autenticación —cada reporte está atado a un
usuario— pero **no verifico que la foto se tomó donde dice**. La mitigación sería
contrastar los metadatos EXIF con las coordenadas, y está en la deuda documentada.

## Sobre seguridad y privacidad

**¿Están cifrados los datos?**
Sí, en tránsito y en reposo, en los dos modos de despliegue. Lo que decide la variable
`use_customer_managed_key` es quién custodia la clave: con clave propia tengo política de
clave y rotación auditable, y cuesta un dólar al mes; con las claves de AWS el dato sigue
cifrado sin ese cargo. Está en `false` para el piloto y se activa en producción.

**¿Qué datos personales manejan?**
Los mínimos: ningún nombre, ninguna cédula, ningún teléfono. La única identidad es un
identificador opaco de Cognito. Pero soy consciente de que un reporte dice implícitamente
dónde estuvo una persona y a qué hora, así que lo trato como dato sensible: en los logs el
usuario aparece como hash, la API nunca devuelve el identificador, y todo caduca
automáticamente a los 540 días.

**¿Y las personas que salen en las fotos?**
Es una debilidad reconocida. Hoy no desenfoco rostros ni placas. Antes de cualquier uso
real del corpus habría que hacerlo, y así está planteado en la fase de investigación.

## Sobre la implementación

**¿Esto funciona o es solo un diseño?**
[Ajuste según su caso.] *Si desplegó:* funciona, acaban de verlo, y aquí está el tablero
de CloudWatch con las métricas reales. *Si no desplegó:* la infraestructura está completa
en Terraform y se despliega con un comando; lo que puedo demostrar hoy son las 112 pruebas
automatizadas que ejercitan toda la lógica de negocio.

**¿Cuánto de esto probaste?**
112 pruebas automatizadas, 82 % de cobertura, con el dominio y la capa de servicios al
100 %. Lo no cubierto es el código que solo se ejecuta contra AWS real. Y sé que las
pruebas sirven porque encontraron un defecto real: la API estaba filtrando el
identificador del usuario.

**¿Funciona sin internet?**
El reporte se captura sin conexión y se guarda en el dispositivo; se envía solo cuando
vuelve la señal. Fue una decisión deliberada: los puntos críticos suelen estar donde peor
llega la red, y perder el reporte después de que el ciudadano se tomó el trabajo de
capturar la evidencia es la forma más segura de que no vuelva a usar la app.

## Sobre el alcance y la continuidad

**¿Quién usaría esto realmente?**
Dos actores: el ciudadano que reporta y el operador de aseo que prioriza. El modelo de
adopción realista es a través de juntas de acción comunal, que ya tienen el canal
organizado con los vecinos.

**¿Cómo se sostiene en el tiempo?**
Técnicamente, el costo operativo es marginal. El reto real no es técnico sino de
participación, y lo reconozco como riesgo en la propuesta: si nadie reporta, no hay
sistema. Por eso el objetivo de los 60 segundos no es cosmético.

**Si tuvieras dos meses más, ¿qué harías?**
Tres cosas, en este orden: el piloto de campo para validar contra el inventario oficial,
el desenfoque de rostros —porque bloquea cualquier uso real del corpus— y el clasificador
propio en el dispositivo, que elimina el 62 % del costo y mejora la pertinencia de las
categorías al contexto colombiano.

---

## Errores que conviene evitar

| Error | En su lugar |
|---|---|
| Leer las diapositivas | Las diapositivas son el apoyo; el contenido lo pone usted |
| Enumerar servicios de AWS | Explicar la decisión detrás de cada uno |
| Decir "no alcancé a hacer X" | "X está documentado como limitación y esta es la mitigación" |
| Depurar en vivo si algo falla | Pasar a la captura en `docs/evidencias/` y seguir |
| Inventar una respuesta | "No lo medí. Lo que sí puedo decir es…" — un jurado detecta el relleno |
| Terminar con "eso es todo" | Cerrar invitando a preguntas |

---

Anterior: [Referencia de la API](09-api.md)
