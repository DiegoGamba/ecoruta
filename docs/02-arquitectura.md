# 2. Arquitectura de la solución

## 2.1 Vista general

```mermaid
flowchart TB
    subgraph Cliente["Dispositivo del ciudadano"]
        APP["App Flutter<br/>Android · iOS"]
    end

    subgraph Borde["Borde de la nube"]
        COG["Amazon Cognito<br/>User Pool + grupos"]
        APIGW["API Gateway HTTP API<br/>Autorizador JWT · throttling"]
    end

    subgraph Computo["Cómputo · AWS Lambda (Python 3.12, arm64)"]
        L1["create_report"]
        L2["get_report"]
        L3["update_status"]
        L4["hotspots"]
        L5["indicators"]
        L6["presign_evidence"]
        L7["classify_evidence"]
        L8["notify_operator"]
    end

    subgraph Datos["Persistencia"]
        DDB[("DynamoDB<br/>single-table + 3 GSI")]
        S3[("S3<br/>evidencias cifradas")]
    end

    subgraph Async["Integración asíncrona"]
        EB["EventBridge"]
        SNS["SNS"]
        DLQ["SQS DLQ"]
    end

    REK["Amazon Rekognition"]
    CW["CloudWatch · X-Ray"]

    APP -->|"1 . autenticación SRP"| COG
    APP -->|"2 . JWT en cada petición"| APIGW
    COG -.->|"valida token"| APIGW
    APIGW --> L1 & L2 & L3 & L4 & L5 & L6

    L6 -->|"3 . URL prefirmada"| APP
    APP ==>|"4 . PUT directo de la foto"| S3
    S3 -->|"5 . evento ObjectCreated"| L7
    L7 --> REK
    L7 --> DDB

    L1 & L3 --> DDB
    L2 & L4 & L5 --> DDB
    L1 -->|"6 . ReporteCreado"| EB
    EB --> L8
    EB -.->|"fallos"| DLQ
    L8 --> SNS
    SNS -->|"7 . alerta"| OP["Operador de aseo"]

    Computo -.-> CW
    APIGW -.-> CW
```

## 2.2 Decisiones estructurales

### Una función por caso de uso

Cada endpoint se despliega como una Lambda independiente en lugar de un monolito con
enrutamiento interno. El costo es más recursos que declarar; el beneficio, tres
propiedades que importan:

- **Permisos de mínimo privilegio reales.** `get_report` solo puede leer DynamoDB;
  `presign_evidence` solo puede firmar objetos en un prefijo del bucket y no toca la
  base de datos. Un monolito obligaría a unir todos los permisos en un rol.
- **Aislamiento de fallos.** Un error en la clasificación de imágenes no afecta la
  creación de reportes.
- **Métricas por endpoint sin instrumentación adicional.** Duración, errores y
  concurrencia llegan separados desde CloudWatch.

En el código, esto no duplica lógica: los handlers son adaptadores delgados sobre una
capa `services` compartida que no conoce HTTP ni AWS.

### Capas y dirección de dependencias

```
handlers/   adaptadores HTTP y de eventos  ─┐
                                             ├─► services/     casos de uso
common/http, config, logging  ──────────────┘        │
                                                      ▼
                                            repository/  (Protocol)
                                              ├── DynamoReportRepository
                                              └── InMemoryReportRepository  (pruebas)
                                                      │
                                            models/ + geo/   dominio puro
```

Las dependencias apuntan siempre hacia el dominio. Consecuencia práctica: las 112 pruebas
unitarias corren sin credenciales de AWS, sin red y en menos de un segundo, porque la
lógica de negocio se ejercita contra el repositorio en memoria.

### Modelo de datos: una sola tabla

Ver [modelo de datos](03-modelo-datos.md) para el detalle de claves e índices. La idea
central: cada consulta del producto se resuelve con un `Query` sobre una clave conocida,
nunca con un `Scan`. Los tres índices existen porque hay exactamente tres preguntas:
*¿qué hay cerca de aquí?* (GSI1, geohash), *¿qué está pendiente?* (GSI2, estado) y
*¿a qué reporte pertenece esta foto?* (GSI3, disperso sobre `evidence_key`).

### La foto no atraviesa el cómputo

`presign_evidence` devuelve una URL prefirmada y el dispositivo hace `PUT` directo a S3.
Esto evita el límite de 6 MB de payload de Lambda, elimina el costo de transferir la
imagen dos veces y reduce el tiempo de respuesta percibido. La URL vive 5 minutos, está
restringida a un tipo MIME de la lista blanca, a un tamaño máximo y a una clave que
incluye el hash del usuario, de modo que un enlace filtrado no permite escribir en
cualquier parte del bucket.

### Publicación de eventos en vez de llamadas directas

`create_report` no llama a la Lambda de notificación: publica `ReporteCreado` en
EventBridge. Añadir mañana un consumidor —un panel en tiempo real, una integración con
el sistema de rutas del operador, un pipeline de investigación— es agregar una regla,
sin tocar el código que ya funciona. Los eventos que fallan tras tres reintentos caen en
una DLQ con alarma, así que ningún reporte se pierde en silencio.

## 2.3 Flujo detallado del reporte

```mermaid
sequenceDiagram
    autonumber
    participant U as Ciudadano
    participant A as App Flutter
    participant G as API Gateway
    participant P as presign_evidence
    participant S as S3
    participant C as create_report
    participant D as DynamoDB
    participant E as EventBridge
    participant K as classify_evidence
    participant N as notify_operator

    U->>A: toma foto y elige categoría
    A->>A: comprime imagen y resuelve GPS
    A->>G: POST /evidencias/url (JWT)
    G->>P: invoca (token ya validado)
    P-->>A: URL prefirmada (5 min)
    A->>S: PUT imagen cifrada (KMS)
    A->>G: POST /reportes {lat, lon, categoría, evidence_key}
    G->>C: invoca
    C->>C: valida y calcula geohash
    C->>D: PutItem (condición: no duplicado)
    C->>E: publica ReporteCreado
    C-->>A: 201 Created
    S-->>K: ObjectCreated
    K->>K: Rekognition DetectLabels
    K->>D: UpdateItem (ai_labels, ai_category)
    E-->>N: ReporteCreado
    N->>N: ¿peligroso o severidad ≥ 4?
    N-->>U: alerta al operador (SNS)
```

Nota sobre el orden: la app sube la foto **antes** de crear el reporte, de modo que
`evidence_key` ya existe cuando se persiste el registro. Si la clasificación llega antes
que el reporte (carrera posible), `classify_evidence` no encuentra el reporte en GSI3,
lo registra y no falla — el dato de IA es un enriquecimiento, no un requisito.

## 2.4 Algoritmo de agrupamiento

El endpoint `/puntos-criticos` convierte reportes sueltos en puntos críticos:

1. **Prefiltrado por geohash (GSI1).** Se consultan la celda del punto y sus vecinas a
   precisión 6 (≈ 1,2 km). Esto acota el conjunto a decenas de reportes sin escanear la
   tabla.
2. **Agrupamiento por densidad.** Variante de DBSCAN sobre distancia de Haversine: cada
   reporte no asignado abre un grupo y absorbe a los que estén dentro del radio
   (120 m por defecto, configurable entre 30 y 1000 m).
3. **Umbral de existencia.** Un grupo se considera punto crítico solo con 3 o más
   reportes. Evita que una queja aislada movilice una cuadrilla.
4. **Priorización.** Cada grupo recibe una severidad acumulada (suma de severidades
   declaradas) y se ordena de mayor a menor. La categoría dominante define el protocolo
   de manejo.

Solo entran al análisis los reportes en estado `reportado` o `verificado`: lo ya atendido
no debe seguir apareciendo como punto activo.

## 2.5 Estados del reporte

```mermaid
stateDiagram-v2
    [*] --> reportado: ciudadano crea
    reportado --> verificado: operador confirma
    reportado --> descartado: falso positivo
    verificado --> programado: se asigna cuadrilla
    verificado --> descartado
    programado --> atendido: intervención ejecutada
    atendido --> [*]
    descartado --> [*]
```

Las transiciones se validan en el servidor (`validate_status_transition`); no hay saltos
ni retrocesos. Un reporte no puede pasar de `reportado` a `atendido` sin verificación,
que es justamente el control que da confiabilidad al indicador de atención.

## 2.6 Atributos de calidad

| Atributo | Cómo se logra |
|---|---|
| **Escalabilidad** | Cómputo sin servidor con concurrencia automática; DynamoDB bajo demanda; sin cuello de botella compartido |
| **Disponibilidad** | Servicios administrados multi-AZ por defecto; ninguna instancia propia que mantener |
| **Seguridad** | JWT validado en el borde, IAM por función, cifrado en reposo, TLS obligatorio, MFA opcional |
| **Observabilidad** | Logs JSON estructurados, trazas X-Ray, 11 alarmas, tablero operativo |
| **Mantenibilidad** | Capas con dependencias hacia el dominio, 112 pruebas, linting y análisis de seguridad en CI |
| **Costo** | Escala a cero; ARM64 (~20 % menos por invocación); ciclo de vida de S3 hacia clases frías |
| **Resiliencia** | Cola local en el dispositivo, reintentos con DLQ, escrituras idempotentes por condición |

## 2.7 Costo de operación

El costo se analiza en dos escenarios, porque son decisiones distintas: validar la
solución y operarla.

### Escenario A — Piloto académico (lo que cuesta demostrarla)

Un despliegue de demostración —decenas de reportes, un evaluador probando la app—
cae **íntegramente dentro de la capa gratuita de AWS**:

| Servicio | Capa gratuita aplicable | Consumo de la demo | Costo |
|---|---|---|---|
| Lambda | 1 M invocaciones y 400.000 GB-s al mes, **permanente** | < 500 invocaciones | 0,00 |
| DynamoDB | 25 GB de almacenamiento, **permanente** | < 1 MB | 0,00 |
| API Gateway HTTP | 1 M peticiones/mes durante 12 meses | < 500 | 0,00 |
| S3 | 5 GB y 2.000 PUT durante 12 meses | < 20 MB | 0,00 |
| Cognito | Usuarios activos mensuales sin costo hasta el umbral gratuito | 2 usuarios | 0,00 |
| Rekognition | **1.000 imágenes/mes** (APIs de Grupo 2) durante 12 meses | < 30 imágenes | 0,00 |
| SNS | 1 M publicaciones y 1.000 correos al mes | < 10 | 0,00 |
| CloudWatch | 10 alarmas y 5 GB de logs al mes | 11 alarmas ⚠ | ~0,10 |
| EventBridge | Sin capa gratuita: 1 USD por millón de eventos | < 500 eventos | ~0,00 |

**Total de la demostración: prácticamente cero.** El único renglón facturable es la
alarma número 11, unos diez centavos de dólar al mes.

> **Decisión de diseño asociada.** La variable `use_customer_managed_key` viene en
> `false` por defecto. Una clave KMS propia cuesta 1 USD/mes de custodia,
> independientemente del uso; con `false` los datos siguen cifrados en reposo con las
> claves administradas por AWS, que no tienen ese cargo. Se activa en producción, donde
> el control de la política de clave y su rotación auditable sí justifican el costo.
> Ver [ADR-009](05-decisiones-adr.md).

Para no gastar nada al terminar: `terraform destroy` elimina todo lo creado.

### Escenario B — Publicar y operar la aplicación durante un año

El costo de una solución móvil no es solo el del backend: publicar en las tiendas tiene
sus propias tarifas, y son las que dominan el primer año.

| Concepto / servicio móvil | Proveedor | Frecuencia | Costo USD |
|---|---|---|---|
| Google Play Console | Google | Pago único | 25,00 |
| Apple Developer Program | Apple | Suscripción anual | 99,00 |
| Backend serverless (Lambda, API Gateway, DynamoDB, S3) | AWS | Mensual × 12 | 2,88 |
| Clasificación de imágenes (Rekognition) | AWS | Mensual × 12 | 36,00 |
| Notificaciones push (SNS) | AWS | Mensual × 12 | 1,20 |
| Observabilidad (CloudWatch, EventBridge) | AWS | Mensual × 12 | 6,00 |
| Mapas (OpenStreetMap) | OSMF | — | 0,00 |
| **Total primer año** | | | **170,08** |
| **Total años siguientes** (sin el pago único de Play) | | | **145,08** |

Contra un presupuesto asignado de **300 USD**, el primer año consume el **56,7 %** y deja
**43,3 % libre**.

Dos decisiones explican esas cifras:

- **Mapas con OpenStreetMap en lugar del SDK de Google Maps.** Google Maps cobra por carga
  de mapa superado el crédito mensual; para una aplicación cuya pantalla principal *es* un
  mapa, ese renglón crecería con el uso. OpenStreetMap no tiene ese costo, a cambio de una
  cartografía algo menos detallada en zonas periféricas —justamente donde el proyecto
  opera, así que conviene vigilarlo.
- **Rekognition es el 21 % del total anual** y el único renglón que escala con los
  reportes. Sustituirlo por un clasificador propio ejecutado en el dispositivo lo llevaría
  a cero; es el argumento económico de la línea de investigación.

Si solo se publica en Android, el primer año baja a **71,08 USD**: los 99 USD anuales de
Apple son la barrera de entrada más costosa para un piloto académico.

### Escenario C — Operación del backend a escala real

Una localidad con 3.000 reportes/mes, 30.000 consultas de mapa/mes y foto promedio de
400 KB, ya fuera de la capa gratuita:

| Servicio | Consumo mensual | Costo estimado (USD) |
|---|---|---|
| Lambda | ~40.000 invocaciones, 512 MB, ~200 ms | 0,05 |
| API Gateway HTTP | ~40.000 peticiones | 0,04 |
| DynamoDB (bajo demanda) | ~50.000 lecturas + 6.000 escrituras | 0,10 |
| S3 | 1,2 GB acumulados + PUT | 0,05 |
| Rekognition | 3.000 imágenes a 1 USD por millar | 3,00 |
| EventBridge, SNS, CloudWatch | volumen bajo | 0,60 |
| KMS (clave propia, ya en producción) | 1 clave | 1,00 |
| **Total aproximado** | | **≈ 4,85 USD/mes** |

El componente dominante es Rekognition: **el 62 % del costo operativo**. Esto refuerza
la línea de investigación —un clasificador propio, ligero y ejecutado en el dispositivo,
eliminaría ese renglón completo además de mejorar la pertinencia de las categorías al
contexto colombiano.

---

Anterior: [Análisis del problema](01-analisis-problema.md) ·
Siguiente: [Modelo de datos](03-modelo-datos.md)
