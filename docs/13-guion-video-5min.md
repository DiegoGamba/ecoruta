# 13. Guion del video de sustentación · 5 minutos

Guion cerrado para la **Entrega 2**. Léalo tal cual: está cronometrado.

> **Requisitos de la entrega:** video 16:9 horizontal, alojado en **YouTube en modo
> público**, de **3 a 5 minutos**, con miniatura personalizada.
> Excederse del rango castiga el criterio de Control del Tiempo (15 %).

**Duración total: 4 min 50 s.** Deja 10 segundos de margen.

---

## Reparto del tiempo, según el peso de la rúbrica

| Bloque | Tiempo | Criterio que alimenta | Peso |
|---|---|---|---|
| 1 · Apertura y problema | 0:00 – 0:45 | Comunicación y narrativa | 20 % |
| 2 · Arquitectura Cloud | 0:45 – 2:05 | **Dominio técnico Cloud** | 25 % |
| 3 · Demostración en vivo | 2:05 – 3:25 | **Demostración y GitHub** | 25 % |
| 4 · Defensa de decisiones | 3:25 – 4:15 | Argumentación técnica | 15 % |
| 5 · Cierre y semillero | 4:15 – 4:50 | Potencial institucional | 15 % |

Los dos bloques centrales valen la mitad de la nota. Si algo hay que recortar en la
grabación, se recorta del bloque 1, nunca del 2 ni del 3.

---

## Antes de grabar

```bash
cd ~/Documents/ecoruta
python3 demo/local_server.py
```

Cuatro pestañas listas, en este orden:

1. `http://localhost:8000` — la demostración corriendo, con el mapa cargado
2. `https://github.com/DiegoGamba/ecoruta` — el repositorio
3. La presentación en pantalla completa (`presentacion/EcoRuta-presentacion.pdf`)
4. `https://github.com/DiegoGamba/ecoruta/actions` — el CI en verde

Grabe la pantalla en **16:9 a 1080p**, con audio del micrófono. Silencie notificaciones.
Haga una prueba de 20 segundos y escúchela antes de grabar en serio.

---

## BLOQUE 1 · Apertura y problema · 0:00 – 0:45

*(Diapositiva 1, luego 2)*

> Somos Diego Gamba y Mariana Diez, y presentamos **EcoRuta**: una aplicación móvil multiplataforma en Flutter,
> respaldada por una arquitectura serverless en AWS, para el reporte ciudadano y la
> priorización automática de puntos críticos de residuos sólidos.
>
> El problema es conocido: hay una esquina en cada barrio donde aparece basura, la recogen,
> y a la semana reaparece media cuadra más allá. Los inventarios que levantan las entidades
> de aseo quedan desactualizados en semanas, y los canales de reporte actuales —la línea
> telefónica, el formulario web— producen texto libre, sin coordenadas y sin evidencia. Eso
> obliga a verificar en campo antes de mandar una cuadrilla.
>
> La pregunta que guía el proyecto es: **¿de qué manera una app en Flutter con captura
> georreferenciada y sincronización offline-first permite reportar un punto crítico en menos
> de 60 segundos, con más del 95 % de envíos exitosos en zonas de baja conectividad?**

⏱ *Debe ir en 0:45. Si va tarde, entre directo al bloque 2.*

---

## BLOQUE 2 · Arquitectura Cloud · 0:45 – 2:05

*(Diapositiva 5. Este bloque vale el 25 %: hable de decisiones, no de una lista de servicios.)*

> Esta es la arquitectura. Cuatro capas, y en cada una tomé una decisión que quiero
> justificar.
>
> **En el borde, Cognito y API Gateway.** Quien valida el token JWT es API Gateway, no mi
> código: una petición sin credenciales válidas **nunca llega a ejecutar una función mía**.
> La app es un cliente público sin secreto, porque un secreto embebido en un APK que
> distribuyo no es un secreto.
>
> **En el cómputo, ocho funciones Lambda en Python, una por caso de uso.** Pude hacer un
> monolito con enrutamiento interno; las separé para tener **mínimo privilegio real**: la
> función que consulta un reporte solo puede leer, y la que firma la subida de fotos ni
> siquiera toca la base de datos. Son ocho roles de IAM, uno por función. Corren en ARM64,
> que cuesta cerca de un 20 % menos por invocación.
>
> **En los datos, una sola tabla de DynamoDB con tres índices.** Ninguna operación de la
> aplicación usa `Scan`: cada consulta se resuelve por una clave conocida, a costo
> constante. La clave de partición del índice geográfico es un **geohash**, que convierte
> una coordenada en una cadena donde los puntos cercanos comparten prefijo.
>
> **Y una decisión que quiero destacar: la fotografía no atraviesa mi capa de cómputo.** La
> app pide una URL prefirmada y sube directo a S3. Eso evita el límite de seis megabytes de
> Lambda, ahorra transferir la imagen dos veces y hace que la app nunca maneje credenciales
> de AWS.
>
> Todo esto está declarado en **Terraform**: 43 recursos, ninguno creado a mano.

⏱ *Debe ir en 2:05.*

---

## BLOQUE 3 · Demostración en vivo · 2:05 – 3:25

**Cambie a la pestaña de la demostración. Esto vale el otro 25 %: navegue el sistema, no
muestre capturas.**

> Voy a demostrarlo corriendo directo desde el repositorio. Aclaro qué estoy ejecutando:
> este es **el mismo código Python que se despliega en las Lambdas** —la validación, el
> geohash, el agrupamiento espacial, los indicadores—. Lo único que sustituí es DynamoDB,
> por el repositorio en memoria que usan las pruebas, para poder demostrarlo sin depender
> de una cuenta de nube.

**Señale el panel izquierdo.**

> Arriba, los indicadores operativos. En el mapa, cada círculo es un **punto crítico**: un
> grupo de reportes que el algoritmo juntó porque están a menos de 120 metros entre sí. El
> número es cuántos reportes lo forman y el color es la prioridad, que sale de la severidad
> acumulada.
>
> Hay algo que **no** se ve y es igual de importante: los datos incluyen doce reportes
> aislados por toda la ciudad, y ninguno aparece. Un grupo solo es punto crítico con **tres
> o más reportes**. Sin ese umbral, una queja aislada movilizaría una cuadrilla.

**Haga clic en un punto vacío del mapa → Enviar reporte. Repita en el MISMO punto.**

> Reporto. Fijo la ubicación, elijo el tipo de residuo, la severidad, y envío. El servidor
> validó la entrada y calculó el geohash… pero no apareció ningún punto crítico: un reporte
> solo no lo es.
>
> Segundo reporte en el mismo lugar. Sigue sin aparecer.

**Envíe el tercero.**

> Y al tercero **aparece el punto crítico**, y los indicadores suben. Eso es el umbral
> funcionando en vivo.

⏱ *Debe ir en 3:25. Practique esta secuencia dos veces antes de grabar.*

---

## BLOQUE 4 · Defensa de decisiones · 3:25 – 4:15

*(Diapositiva 8, luego 10)*

> El agrupamiento es una variante de **DBSCAN sobre distancia de Haversine**, con
> prefiltrado por geohash para no escanear la ciudad entera. Elegí DBSCAN y no k-means
> porque k-means exige decidir de antemano cuántos grupos hay, y yo no sé cuántos puntos
> críticos tiene una localidad: justamente eso es lo que quiero descubrir.
>
> También descarté opciones con criterio: consideré **PostgreSQL con PostGIS**, superior
> para consultas espaciales complejas, pero mis consultas reales son "qué hay cerca de este
> punto" —que el geohash resuelve a costo constante— y PostGIS obligaba a una instancia
> siempre encendida dentro de una VPC, que por sí sola costaría más que toda la solución.
>
> El proyecto tiene **112 pruebas automatizadas** y 82 % de cobertura, que corren en cada
> push junto con análisis estático y de seguridad. Y sé que sirven porque **encontraron un
> defecto real**: la API estaba devolviendo el identificador del usuario junto con el
> reporte. Una fuga de datos personales que no se ve leyendo el código, solo se ve cuando
> alguien la prueba.
>
> Publicar y operar la app el primer año cuesta **170 dólares** contra un presupuesto de
> 300 —y dos terceras partes de eso son las tarifas de Google Play y Apple, no
> infraestructura—.

⏱ *Debe ir en 4:15.*

---

## BLOQUE 5 · Cierre y semillero · 4:15 – 4:50

*(Diapositiva 12, luego 14)*

> Sobre el estado del proyecto, quiero ser preciso: la lógica de negocio funciona y acaban
> de verla; la infraestructura está completa en Terraform y validada en el pipeline; las
> pruebas en dispositivos reales son el paso que sigue.
>
> Y hay una línea de investigación abierta: existe literatura sobre reporte ciudadano
> ambiental, y existe sobre clasificación automática de residuos, pero es escasa la
> evidencia sobre **las dos cosas juntas en ciudades latinoamericanas**. La primera fase es
> un experimento concreto: contrastar los puntos críticos que produce la app contra el
> inventario oficial publicado como dato abierto, y medir precisión y exhaustividad.
>
> Todo está en el repositorio público: código, infraestructura, doce documentos técnicos y
> esta presentación. Muchas gracias.

⏱ *Cierre en 4:50.*

---

## Después de grabar

- [ ] El video dura **entre 3:00 y 5:00** — verifíquelo antes de subir
- [ ] Está en **16:9 horizontal**
- [ ] Subido a YouTube en modo **Público** (no "oculto", no "privado")
- [ ] Miniatura personalizada cargada (`presentacion/miniatura/miniatura-youtube.png`,
      con su foto o avatar ya incrustado)
- [ ] Título del video: *EcoRuta — Sustentación técnica · Diseño de Aplicaciones Móviles*
- [ ] Si exponen los dos, repártanse los bloques: uno toma 1 y 2, el otro 3 y 4, y cierran juntos
- [ ] En la descripción: el enlace al repositorio
- [ ] Entregue el **enlace de YouTube** en el buzón de Canvas

## Errores que cuestan nota

| Error | Consecuencia |
|---|---|
| Pasarse de 5 minutos | Control del Tiempo baja a 2.0 (15 % de la nota) |
| Leer las diapositivas en voz alta | Comunicación baja a 3.0 |
| Mostrar capturas en vez de navegar el sistema | Demostración baja a 3.0 |
| Decir que está desplegado en AWS o que la app corre en un teléfono | Es falso: contradice el repositorio y castiga Dominio Técnico |
| Video en YouTube como "oculto" o "privado" | Incumplimiento técnico de la entrega |

---

Anterior: [Respuestas a la guía del taller](12-guia-taller.md)
