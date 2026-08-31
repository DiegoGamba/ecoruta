# 3. Modelo de datos

## 3.1 Diseño single-table

Una sola tabla de DynamoDB (`ecoruta-<stage>-reportes`) con claves genéricas. El
razonamiento: en DynamoDB el modelo se diseña desde las consultas, no desde las
entidades. Aquí las consultas son cuatro y cada una tiene su clave.

| Consulta del producto | Índice | Clave de partición | Clave de orden |
|---|---|---|---|
| Detalle de un reporte | Tabla principal | `REPORT#<uuid>` | `METADATA` |
| Reportes cerca de un punto | GSI1 | `GEO#<geohash6>` | `<created_at>#<uuid>` |
| Bandeja por estado | GSI2 | `STATUS#<estado>` | `<created_at>` |
| Reporte dueño de una foto | GSI3 (disperso) | `EVID#<evidence_key>` | `<created_at>` |

Ninguna operación de la aplicación usa `Scan`.

## 3.2 Estructura del ítem

```json
{
  "PK": "REPORT#8f3c2b1a-...",
  "SK": "METADATA",
  "GSI1PK": "GEO#d2g6cx",
  "GSI1SK": "2026-08-31T14:22:05+00:00#8f3c2b1a-...",
  "GSI2PK": "STATUS#reportado",
  "GSI2SK": "2026-08-31T14:22:05+00:00",
  "GSI3PK": "EVID#evidencias/2026/08/31/a3f1c9d2e4b7/....jpg",
  "GSI3SK": "2026-08-31T14:22:05+00:00",

  "entity": "Report",
  "report_id": "8f3c2b1a-...",
  "user_id": "e4f8a2c1-...",
  "lat": 4.710989,
  "lon": -74.072092,
  "geohash": "d2g6cxp",
  "category": "escombros",
  "severity": 4,
  "description": "acumulación en el andén frente al parque",
  "status": "reportado",
  "evidence_key": "evidencias/2026/08/31/a3f1c9d2e4b7/....jpg",
  "locality": "Suba",
  "ai_labels": ["Rubble", "Brick", "Concrete"],
  "ai_category": "escombros",
  "created_at": "2026-08-31T14:22:05+00:00",
  "updated_at": "2026-08-31T14:22:05+00:00",
  "ttl": 1804161725
}
```

## 3.3 Notas de diseño

**Geohash a dos precisiones.** El atributo `geohash` se guarda con precisión 7
(celdas de ~153 m, útil para depurar y para futuras agregaciones finas), pero la clave
de partición de GSI1 usa solo los **6 primeros caracteres** (~1,2 km). Es un compromiso
deliberado: una partición por celda de 153 m produciría particiones diminutas y muchas
consultas para cubrir un barrio; una de 1,2 km agrupa lo suficiente para que una sola
consulta traiga el vecindario completo sin volverse una partición caliente.

**GSI3 es disperso.** Los atributos `GSI3PK`/`GSI3SK` solo se escriben cuando el reporte
trae evidencia. DynamoDB únicamente indexa los ítems que tienen la clave, así que el
índice contiene exclusivamente reportes con foto y su proyección es `KEYS_ONLY` —el
mínimo necesario para resolver el `report_id`. Sin este índice, la clasificación tendría
que hacer un `Scan` por cada imagen subida, con costo creciente con el tamaño de la tabla.

**Clave de orden con marca de tiempo.** `GSI1SK` empieza por `created_at` en formato
ISO-8601, que ordena lexicográficamente igual que cronológicamente. Consultar con
`ScanIndexForward=false` devuelve lo más reciente primero sin ordenar en memoria. Se le
concatena el UUID para garantizar unicidad cuando dos reportes comparten segundo.

**Escritura condicional.** `PutItem` incluye `attribute_not_exists(PK)`: un reintento de
la app (por timeout de red, por ejemplo) no puede sobrescribir un reporte existente.

**TTL como minimización de datos.** El atributo `ttl` fija la eliminación automática a
los 540 días. Es simultáneamente una decisión de privacidad —los datos personales
implícitos no se conservan indefinidamente— y de costo. El ciclo de vida del bucket S3
usa el mismo horizonte, de modo que registro y evidencia caducan juntos.

**`user_id` nunca sale de la API.** Se persiste para trazabilidad y para poder atender
una solicitud de supresión, pero `to_public()` y la capa de servicios lo eliminan de toda
respuesta. En los logs aparece únicamente como hash SHA-256 truncado.

## 3.4 Estimación de tamaño

| Elemento | Tamaño |
|---|---|
| Ítem promedio | ~600 bytes |
| 3.000 reportes/mes | ~1,8 MB/mes en la tabla |
| Evidencias (400 KB × 3.000) | ~1,2 GB/mes en S3 |
| Proyección a 540 días | ~32 MB en DynamoDB, ~21 GB en S3 (con transición a clases frías) |

## 3.5 Organización de las evidencias en S3

```
evidencias/<AAAA>/<MM>/<DD>/<hash-usuario>/<uuid>.jpg
```

El prefijo por fecha distribuye la carga de escritura y permite reglas de ciclo de vida
por antigüedad. El segmento de usuario es un hash truncado, no el identificador de
Cognito: quien obtenga la lista de claves no obtiene identidades.

---

Anterior: [Arquitectura](02-arquitectura.md) · Siguiente: [Seguridad](04-seguridad.md)
