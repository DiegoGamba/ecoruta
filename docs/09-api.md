# 9. Referencia de la API

Base: la URL que devuelve `terraform output api_base_url`.
Todas las rutas exigen `Authorization: Bearer <access_token de Cognito>`.
API Gateway valida el token antes de invocar cualquier función.

## Códigos de estado

| Código | Significado |
|---|---|
| 200 / 201 | Operación exitosa |
| 400 | Entrada inválida — el cuerpo indica qué campo y por qué |
| 401 | Token ausente, vencido o inválido (lo emite API Gateway) |
| 403 | Autenticado pero sin el grupo requerido |
| 404 | El reporte no existe |
| 500 | Error interno — la respuesta trae `request_id` para rastrear en CloudWatch |

---

## `POST /reportes`

Crea un reporte. Grupo requerido: ninguno (cualquier usuario autenticado).

**Cuerpo**

| Campo | Tipo | Obligatorio | Reglas |
|---|---|---|---|
| `lat` | número | sí | −90 a 90 |
| `lon` | número | sí | −180 a 180 |
| `category` | texto | no | `escombros`, `organicos`, `reciclables`, `voluminosos`, `peligrosos`. Por defecto `no_clasificado` |
| `severity` | entero | no | 1 a 5. Por defecto 1 |
| `description` | texto | no | máximo 500 caracteres |
| `evidence_key` | texto | no | la clave devuelta por `POST /evidencias/url` |
| `locality` | texto | no | máximo 80 caracteres |

```json
{
  "lat": 4.710989,
  "lon": -74.072092,
  "category": "escombros",
  "severity": 4,
  "description": "acumulación en el andén frente al parque",
  "evidence_key": "evidencias/2026/08/31/a3f1c9d2e4b7/....jpg"
}
```

**201 Created** — cabecera `Location: /reportes/<id>`

```json
{
  "report_id": "8f3c2b1a-...",
  "lat": 4.710989,
  "lon": -74.072092,
  "geohash": "d2g6cxp",
  "category": "escombros",
  "severity": 4,
  "status": "reportado",
  "created_at": "2026-08-31T14:22:05+00:00"
}
```

`user_id` y `ttl` nunca se devuelven.

---

## `GET /reportes/{id}`

Detalle de un reporte. Grupo requerido: ninguno.

---

## `PATCH /reportes/{id}/estado`

Cambia el estado. **Grupo requerido: `operadores`.**

```json
{ "status": "verificado" }
```

Transiciones permitidas:

```
reportado  → verificado | descartado
verificado → programado | descartado
programado → atendido
```

Cualquier otra combinación devuelve 400.

---

## `GET /puntos-criticos`

Agrupa los reportes abiertos cercanos a un punto. Grupo requerido: ninguno.

| Parámetro | Obligatorio | Por defecto | Rango |
|---|---|---|---|
| `lat` | sí | — | −90 a 90 |
| `lon` | sí | — | −180 a 180 |
| `radius_m` | no | 120 | 30 a 1000 (se acota en el servidor) |
| `min_reports` | no | 3 | 2 a 50 |

```json
{
  "center": { "lat": 4.710989, "lon": -74.072092 },
  "params": { "radius_m": 120, "min_reports": 3 },
  "analyzed_reports": 47,
  "hotspot_count": 2,
  "hotspots": [
    {
      "centroid": { "lat": 4.711002, "lon": -74.072118 },
      "geohash": "d2g6cxp",
      "report_count": 7,
      "severity_score": 24,
      "dominant_category": "escombros",
      "category_breakdown": { "escombros": 5, "voluminosos": 2 },
      "report_ids": ["8f3c2b1a-...", "..."]
    }
  ]
}
```

Los puntos vienen ordenados por severidad acumulada descendente. Solo se consideran
reportes en estado `reportado` o `verificado`.

---

## `GET /indicadores`

KPIs operativos. **Grupo requerido: `operadores`.**

```json
{
  "total_reportes": 412,
  "por_estado": {
    "reportado": 88, "verificado": 34, "programado": 12,
    "atendido": 265, "descartado": 13
  },
  "tasa_atencion": 0.6432,
  "pendientes": 134
}
```

---

## `POST /evidencias/url`

Devuelve una URL prefirmada para subir la foto directamente a S3.
Grupo requerido: ninguno.

```json
{ "content_type": "image/jpeg", "size_bytes": 384210 }
```

`content_type` admite `image/jpeg`, `image/png`, `image/webp`.
`size_bytes` debe estar entre 1 y 5 MB.

**201 Created**

```json
{
  "upload_url": "https://ecoruta-dev-evidencias-....s3.amazonaws.com/...",
  "evidence_key": "evidencias/2026/08/31/a3f1c9d2e4b7/....jpg",
  "expires_in": 300
}
```

La subida debe hacerse con `PUT`, el mismo `Content-Type` declarado y la cabecera
`x-amz-server-side-encryption: aws:kms`. La URL caduca a los 5 minutos.

---

## Límites

Throttling por defecto: 50 peticiones/segundo sostenidas, 100 de ráfaga, configurable en
`infra/variables.tf`. Al superarlo, API Gateway responde 429.

---

Anterior: [Guía de despliegue](08-despliegue.md)
