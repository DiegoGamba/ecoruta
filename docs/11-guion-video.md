# 11. Guion para grabar el video de sustentación

Guion cerrado, listo para leer. **Duración objetivo: 9–11 minutos.**

Este documento asume que el proyecto **no está desplegado en AWS** y que la demostración
se hace con el servidor local. Si alcanza a desplegar antes de grabar, la única sección
que cambia es la 5 (ver la variante al final).

---

## Preparación (15 minutos antes de grabar)

**Abra en el navegador, en este orden, y déjelas fijas:**

1. `http://localhost:8000` — la demostración, ya corriendo
2. `https://github.com/DiegoGamba/ecoruta` — el repositorio
3. `https://github.com/DiegoGamba/ecoruta/actions/workflows/ci.yml` — CI en verde
4. La presentación en pantalla completa (`presentacion/EcoRuta-presentacion.pdf`)

**Arranque la demostración:**

```bash
cd ~/Documents/ecoruta
python3 demo/local_server.py
```

**Antes de grabar, verifique:**

- [ ] El mapa carga y se ven cinco círculos numerados
- [ ] Cierre Slack, correo y notificaciones
- [ ] Grabe a 1080p con audio del micrófono, no del sistema
- [ ] Haga una prueba de 20 segundos y escúchela

**Si algo falla en vivo:** no lo arregle frente a la cámara. Pase a
`docs/evidencias/` y siga. Corte y regrabe ese tramo después.

---

## Sección 1 · Presentación · 30 s

*(Diapositiva 1)*

> Buenos días. Soy Diego Gamba y voy a presentar **EcoRuta**: una solución móvil
> respaldada por una arquitectura serverless en AWS para el reporte ciudadano y la
> priorización automática de puntos críticos de residuos sólidos.
>
> El proyecto está publicado en un repositorio público de GitHub con el código, la
> infraestructura como código, la documentación técnica y esta presentación.

---

## Sección 2 · El problema · 1 min 30 s

*(Diapositiva 2)*

> Todos conocemos una esquina del barrio donde aparece basura. La recogen, y a la semana
> vuelve a aparecer media cuadra más allá.
>
> Eso tiene nombre técnico: **punto crítico**. Y tiene tres rasgos que lo hacen difícil
> de atender con los instrumentos actuales.
>
> Primero, **es dinámico**. Los inventarios que levantan las entidades de aseo quedan
> desactualizados en semanas.
>
> Segundo, **es local**. Quien mejor lo detecta es el vecino que pasa por ahí todos los
> días, no el operador que recorre la macro-ruta.
>
> Y tercero, **la información no fluye**. Los canales que existen hoy —la línea
> telefónica, el formulario web, las redes sociales— producen texto libre, sin
> coordenadas y sin evidencia. Eso obliga a mandar a alguien a verificar en campo antes
> de poder programar cualquier intervención.
>
> El resultado es recolección reactiva, riesgo sanitario por vectores y sumideros
> obstruidos. Costos que se podrían evitar.

---

## Sección 3 · La pregunta y la solución · 1 min 30 s

*(Diapositiva 3, luego 4)*

> La pregunta que guía el proyecto es esta: **¿puede un flujo de reporte ciudadano
> georreferenciado, con evidencia fotográfica y agrupamiento espacial automático,
> producir un inventario de puntos críticos más actualizado y accionable que el
> levantamiento manual periódico?**
>
> *(pase a la diapositiva 4)*
>
> La solución tiene cinco pasos. El ciudadano **reporta** con foto, ubicación y
> categoría, en menos de un minuto. El sistema **clasifica** el tipo de residuo desde la
> fotografía. **Agrupa** los reportes cercanos en puntos críticos. Los **prioriza** por
> severidad acumulada. Y el operador **interviene** y cierra el ciclo.
>
> Un detalle de diseño que importa: la app **funciona sin conexión**. Los puntos críticos
> suelen estar donde peor llega la señal, así que si el envío falla, el reporte se guarda
> en el dispositivo y se reintenta solo. Perder el reporte después de que el ciudadano se
> tomó el trabajo de capturar la evidencia es la forma más segura de que no vuelva a usar
> la aplicación.

---

## Sección 4 · La arquitectura · 2 min

*(Diapositiva 5)*

> Esta es la arquitectura. Voy a explicar decisiones, no a enumerar servicios.
>
> **En el borde**, Cognito y API Gateway. La validación del token la hace API Gateway,
> no mi código: una petición sin credenciales válidas **nunca llega a ejecutar una
> función mía**.
>
> **En el cómputo**, ocho funciones Lambda, una por caso de uso. Podría haber hecho un
> monolito con enrutamiento interno; elegí separarlas para tener **mínimo privilegio
> real**. La función que consulta un reporte solo puede leer. La que firma la subida de
> fotos ni siquiera toca la base de datos. Son ocho roles de IAM, uno por función.
>
> **En los datos**, una sola tabla de DynamoDB con tres índices. Ninguna operación de la
> aplicación usa `Scan`: cada consulta del producto se resuelve por una clave conocida.
>
> Y una decisión que quiero señalar: **la fotografía no atraviesa mi capa de cómputo**.
> La aplicación pide una URL prefirmada y sube directo a S3. Eso evita el límite de seis
> megabytes de payload de Lambda, ahorra transferir la imagen dos veces, y hace que la
> app nunca maneje credenciales de AWS.
>
> *(diapositiva 6)*
>
> Cada servicio responde a un rasgo del problema. Y también documenté lo que descarté:
> consideré PostgreSQL con PostGIS, que es técnicamente superior para consultas
> espaciales complejas. Lo descarté porque mis consultas reales son "qué hay cerca de
> este punto", que un prefijo de geohash resuelve a costo constante, mientras que PostGIS
> me obligaba a una instancia siempre encendida dentro de una VPC —que por sí sola
> costaría más que toda la solución.

---

## Sección 5 · Demostración en vivo · 2 min 30 s

**Cambie a la ventana del navegador con la demostración.**

> Voy a mostrar el sistema funcionando. Aclaro qué estoy corriendo: este es el **mismo
> código Python** que se despliega en las Lambdas —la validación, el cálculo de geohash,
> el agrupamiento, los indicadores—. Lo único sustituido es DynamoDB, por el repositorio
> en memoria que usan las pruebas automatizadas, para poder demostrarlo sin depender de
> la nube.

**Señale el panel izquierdo.**

> Arriba están los indicadores operativos: 37 reportes cargados, 34 pendientes, 8 % de
> tasa de atención.
>
> En el mapa, cada círculo es un **punto crítico**: un grupo de reportes que el algoritmo
> juntó porque están a menos de 120 metros unos de otros. El número es cuántos reportes
> lo componen, y el color es la prioridad, que sale de la severidad acumulada.
>
> Hay algo que **no** se ve, y es igual de importante: los datos incluyen doce reportes
> aislados por toda la ciudad. Ninguno aparece en el mapa, porque un grupo solo se
> considera punto crítico con **tres o más reportes**. Sin ese umbral, una queja aislada
> movilizaría una cuadrilla.

**Haga clic en un punto vacío del mapa. Envíe un reporte.**

> Voy a reportar. Hago clic para fijar la ubicación, elijo el tipo de residuo —digamos
> peligrosos—, la severidad, y envío.
>
> El servidor validó la entrada, calculó el geohash —ahí se ve— y lo guardó. Pero no
> apareció ningún punto crítico: **un reporte solo no lo es**.

**Envíe un segundo en el mismo lugar.**

> Segundo reporte. Sigue sin aparecer.

**Envíe el tercero.**

> Y al tercero… **aparece el punto crítico**. Los indicadores subieron de 37 a 40
> reportes. Eso es el umbral funcionando, en vivo.

**Opcional, si quiere lucirse (20 s):** abra las herramientas de desarrollo, pestaña Red.

> Y aquí se ve la respuesta real de la API: el reporte con su geohash, su categoría y su
> estado. Fíjense que **no devuelve el identificador del usuario**: eso lo explico en un
> momento.

---

## Sección 6 · Algoritmo, calidad y seguridad · 2 min

*(Vuelva a la presentación, diapositiva 8)*

> Lo que acaban de ver por dentro es esto. El agrupamiento tiene cuatro pasos:
> prefiltrado por geohash para no escanear la ciudad entera, agrupamiento por densidad
> —una variante de DBSCAN sobre distancia de Haversine—, el umbral de tres reportes, y
> la priorización por severidad acumulada.
>
> Elegí DBSCAN y no k-means porque k-means exige decidir de antemano cuántos grupos hay,
> y yo no sé cuántos puntos críticos tiene una localidad: justamente eso es lo que quiero
> descubrir.
>
> *(diapositiva 10)*
>
> El proyecto tiene **112 pruebas automatizadas** y 82 % de cobertura, con el dominio y
> la capa de servicios al 100 %. Corren sin credenciales de AWS y sin red, porque la
> lógica de negocio no conoce la nube. Corren en cada push, junto con análisis estático y
> análisis de seguridad.
>
> Y sé que las pruebas sirven, porque **encontraron un defecto real**: una de ellas falló
> la primera vez que la ejecuté. La API estaba devolviendo el identificador del usuario
> junto con el reporte. Es una fuga de datos personales que no se ve leyendo el código:
> solo se ve cuando alguien la prueba. Por eso antes les señalé que la respuesta no lo
> incluye.
>
> *(diapositiva 9)*
>
> En seguridad quiero ser explícito con lo que **falta**: no verifico que la foto se haya
> tomado donde dice, no hay WAF, y no desenfoco los rostros de las personas que puedan
> aparecer en las fotografías. Lo documenté como deuda reconocida, porque un análisis de
> seguridad que solo lista lo que sí hice no es un análisis de seguridad.

---

## Sección 7 · Costos y proyección investigativa · 1 min 30 s

*(Diapositiva 11, luego 12)*

> Sobre el costo: la operación real de una localidad completa cuesta menos de cinco
> dólares al mes, y un despliegue de demostración cabe dentro de la capa gratuita de AWS.
> Pero el dato interesante es la composición: **el 62 % es el servicio de visión por
> computador**. Y eso no es un problema de presupuesto, es el argumento de la siguiente
> diapositiva.
>
> *(diapositiva 12)*
>
> Existe literatura sobre reporte ciudadano ambiental, y existe literatura sobre
> clasificación automática de residuos. Es escasa la evidencia sobre **las dos cosas
> juntas en contextos urbanos latinoamericanos**.
>
> La primera fase es un experimento concreto y ejecutable: contrastar los puntos críticos
> que produce la aplicación contra el inventario oficial que las entidades publican como
> dato abierto, y medir precisión y exhaustividad. Eso responde si el reporte ciudadano
> reproduce, anticipa o complementa el levantamiento manual.
>
> La segunda fase es sustituir el clasificador genérico por un modelo propio, entrenado
> con imágenes del contexto local y ejecutado en el dispositivo. Elimina ese 62 % del
> costo y mejora la pertinencia de las categorías.
>
> Y esto no es una lista de deseos: la arquitectura **ya está acumulando** el corpus de
> imágenes y la serie espacio-temporal que esa investigación necesita.

---

## Sección 8 · El repositorio · 45 s

**Cambie a la pestaña de GitHub. Baje por el README.**

> El repositorio es público. Tiene el README con los diagramas de arquitectura, el código
> de la aplicación Flutter, el backend en Python, toda la infraestructura en Terraform
> —43 recursos, ninguno creado a mano—, diez documentos técnicos y la presentación.

**Abra `docs/05-decisiones-adr.md`.**

> Incluí un registro de decisiones de arquitectura: nueve decisiones, cada una con su
> contexto, la alternativa que descarté y las consecuencias, incluidas las negativas.

**Cambie a la pestaña de Actions.**

> Y la integración continua corre en cada push: pruebas, análisis estático, análisis de
> seguridad y validación de la infraestructura. En verde.

---

## Sección 9 · Cierre · 30 s

*(Diapositiva 14)*

> En resumen: el conocimiento local del vecino, convertido en un inventario vivo y
> priorizado.
>
> Un problema real y delimitado. Una arquitectura justificada, con las alternativas
> descartadas por escrito. Ingeniería verificable: 112 pruebas, mínimo privilegio,
> infraestructura como código. Y un camino de investigación abierto y concreto.
>
> Gracias. Quedo atento a sus preguntas.

---

## Variante: si alcanza a desplegar en AWS

Reemplace la aclaración inicial de la **Sección 5** por:

> Voy a mostrar el sistema funcionando sobre la infraestructura real desplegada en AWS.
> Aquí está la consola con las ocho funciones Lambda, la tabla de DynamoDB y el tablero
> de CloudWatch.

Y agregue 30 segundos al final de esa sección:

> Y aquí está el tablero de CloudWatch con las métricas de las peticiones que acabo de
> hacer: latencia, invocaciones y errores, en tiempo real.

---

## Lista de verificación antes de subir el video

- [ ] Se escucha claro y sin eco
- [ ] La demostración funcionó en cámara (o se cortó y regrabó)
- [ ] Se ve el repositorio en vivo, no solo la diapositiva que lo describe
- [ ] Se ve el CI en verde
- [ ] Dijo explícitamente qué es real y qué está sustituido en la demostración
- [ ] Mencionó la deuda de seguridad reconocida
- [ ] Duración entre 9 y 12 minutos

---

Anterior: [Guion de sustentación presencial](10-guion-sustentacion.md)
