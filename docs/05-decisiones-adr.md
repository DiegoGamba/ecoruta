# 5. Registro de decisiones de arquitectura (ADR)

Formato breve: contexto, decisión, consecuencias. Se documentan las decisiones que
serían costosas de revertir.

---

## ADR-001 · Serverless en lugar de contenedores

**Contexto.** El tráfico es muy irregular: picos tras jornadas comunitarias o lluvias,
y actividad casi nula de madrugada. El proyecto no tiene presupuesto de operación
continua ni personal dedicado a infraestructura.

**Decisión.** Lambda + API Gateway HTTP API + DynamoDB bajo demanda. Nada que escale
manualmente, nada encendido sin uso.

**Consecuencias.**
- (+) Costo proporcional al uso: la demostración cabe en la capa gratuita y la
  operación real de una localidad ronda los 5 USD/mes.
- (+) Sin parcheo de sistema operativo ni gestión de red.
- (−) Arranque en frío de 200–400 ms en la primera invocación tras inactividad.
- (−) Acoplamiento al proveedor: migrar exigiría reescribir la capa de adaptadores
  (mitigado porque el dominio no conoce AWS).

---

## ADR-002 · DynamoDB single-table en vez de PostgreSQL + PostGIS

**Contexto.** Las consultas reales son por proximidad geográfica y por estado. PostGIS
resolvería consultas espaciales arbitrarias, pero exige una instancia siempre encendida
dentro de una VPC.

**Decisión.** Una tabla de DynamoDB con geohash como clave de partición del índice
geográfico.

**Consecuencias.**
- (+) Latencia de un dígito de milisegundos y costo constante por consulta.
- (+) Sin VPC, sin NAT Gateway (que por sí solo costaría más que toda la solución).
- (−) No hay consultas espaciales complejas (polígonos, intersecciones); habría que
  añadir un almacén analítico si el proyecto lo requiere.
- (−) El modelo hay que diseñarlo desde las consultas: agregar una consulta nueva puede
  significar un índice nuevo.

---

## ADR-003 · Subida directa a S3 con URL prefirmada

**Contexto.** Las fotos pesan cientos de kilobytes. Pasarlas por API Gateway y Lambda
choca con el límite de 6 MB de payload, duplica la transferencia y encarece la
invocación.

**Decisión.** La API entrega una URL prefirmada de 5 minutos y el dispositivo sube
directo a S3.

**Consecuencias.**
- (+) Menor latencia percibida y menor costo.
- (+) La app nunca maneja credenciales de AWS.
- (−) El flujo tiene dos pasos, y la app debe manejar la falla parcial (foto subida sin
  reporte creado). Se acepta: una evidencia huérfana caduca sola por ciclo de vida.

---

## ADR-004 · Geohash propio en lugar de una librería

**Contexto.** Se necesita codificación de geohash en cada Lambda. Las librerías
disponibles añaden peso al paquete de despliegue.

**Decisión.** Implementar `encode_geohash` (≈40 líneas) dentro del proyecto, con pruebas
contra vectores de referencia conocidos.

**Consecuencias.**
- (+) Paquete liviano, arranque en frío menor, cero dependencias que auditar.
- (+) El algoritmo queda documentado y verificado en el repositorio.
- (−) El mantenimiento es propio. Aceptable: es un algoritmo estable y cubierto por
  pruebas.

---

## ADR-005 · Rekognition como línea base de clasificación

**Contexto.** Clasificar el tipo de residuo desde la foto mejora la calidad del dato,
pero no existe todavía un conjunto de imágenes etiquetadas del contexto local.

**Decisión.** Usar `Rekognition DetectLabels` con un mapeo explícito de etiquetas a las
categorías del dominio, con umbral de confianza del 70 % y precedencia para residuos
peligrosos.

**Consecuencias.**
- (+) Funciona desde el primer día sin datos de entrenamiento.
- (+) El mapeo es una tabla legible y comprobable, no una caja negra.
- (−) Es el componente más caro: el 62 % del costo operativo. En la demostración no
  cuesta nada (1.000 imágenes/mes gratuitas durante 12 meses).
- (−) Las etiquetas son genéricas y no conocen el contexto colombiano.
- **Camino de evolución.** Sustituirlo por un modelo propio entrenado con las evidencias
  acumuladas es la principal línea de investigación del proyecto; Rekognition queda como
  línea base contra la cual comparar.

---

## ADR-006 · Una Lambda por caso de uso

**Contexto.** La alternativa habitual es un monolito con enrutamiento interno, que
reduce el número de recursos a declarar.

**Decisión.** Ocho funciones independientes, con lógica compartida en la capa `services`.

**Consecuencias.**
- (+) Mínimo privilegio efectivo: cada rol lista solo lo que su función usa.
- (+) Fallos aislados y métricas por endpoint sin instrumentación adicional.
- (−) Más recursos en Terraform (resuelto con `for_each` sobre un mapa declarativo).
- (−) Más superficies de arranque en frío.

---

## ADR-007 · Cola local de reportes en el dispositivo

**Contexto.** Los puntos críticos suelen estar donde la conectividad es peor. Perder el
reporte tras capturar la evidencia es la forma más segura de que el ciudadano no vuelva
a usar la app.

**Decisión.** Ante un fallo de red o un 5xx, el reporte se persiste localmente y se
reintenta al abrir la app.

**Consecuencias.**
- (+) El trabajo del ciudadano nunca se pierde.
- (−) El reporte puede llegar con retraso; `created_at` lo asigna el servidor al recibir.
- (−) Los rechazos por validación (4xx) se descartan de la cola para no bloquearla
  indefinidamente.

---

## ADR-008 · Terraform con estado remoto y OIDC

**Contexto.** La infraestructura debe ser reproducible y auditable, y el despliegue
automático no debería requerir llaves de AWS de larga vida.

**Decisión.** Terraform con backend S3 y bloqueo, y GitHub Actions autenticándose contra
AWS por OIDC.

**Consecuencias.**
- (+) Toda la infraestructura es revisable en un pull request.
- (+) Cero secretos de AWS almacenados en GitHub.
- (−) Requiere un paso de arranque manual (crear el bucket de estado y el rol OIDC),
  documentado en el README.

---

## ADR-009 · Clave KMS propia opcional, desactivada por defecto

**Contexto.** El diseño original cifraba DynamoDB, S3, los logs, SNS y SQS con una clave
KMS propia del proyecto. Una clave administrada por el cliente cuesta 1 USD/mes de
custodia, se cobre o no uso alguno. Ese cargo fijo es el único renglón que impedía
desplegar el proyecto a costo cero, y convertía una demostración académica de dos días
en una suscripción.

**Decisión.** Introducir `use_customer_managed_key`, con valor por defecto `false`.
Con `false` cada servicio usa la clave administrada por AWS correspondiente
(`alias/aws/sqs`, `alias/aws/sns`, cifrado propio de S3 con AES256, clave de AWS en
DynamoDB); con `true` se crea la clave del proyecto y todos los recursos la usan.

**Consecuencias.**
- (+) El despliegue de demostración cuesta prácticamente cero: los datos siguen cifrados
  en reposo en ambos modos, porque lo que cambia es **quién custodia la clave**, no si
  hay cifrado.
- (+) La diferencia queda explícita y argumentada, en vez de escondida en un valor fijo.
- (−) Con `false` se pierde lo que justifica una clave propia en producción: política de
  clave propia, rotación anual auditable, revocación independiente de AWS y registro de
  cada uso en CloudTrail bajo la clave del proyecto.
- (−) El algoritmo de cifrado del bucket pasa a ser información que el cliente necesita
  al subir la evidencia. Se resolvió haciendo que la API devuelva las cabeceras exactas
  en `required_headers`: la app deja de asumir cómo está cifrado el bucket, lo que además
  elimina un acoplamiento que ya existía.

**Cuándo revertir.** En producción, o ante cualquier requisito de cumplimiento sobre
custodia de claves: `use_customer_managed_key = true` en el `.tfvars` del ambiente.

---

Anterior: [Seguridad](04-seguridad.md) ·
Siguiente: [Pruebas y resultados](06-pruebas-resultados.md)
