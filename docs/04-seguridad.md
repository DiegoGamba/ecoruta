# 4. Seguridad y privacidad

## 4.1 Modelo de amenazas (STRIDE abreviado)

| Amenaza | Escenario concreto | Control implementado |
|---|---|---|
| **Suplantación** | Alguien reporta a nombre de otro ciudadano | Cognito con SRP y MFA opcional; el `sub` del JWT es la única fuente de identidad, nunca un campo del cuerpo |
| **Manipulación** | Un ciudadano marca su propio reporte como "atendido" | Las transiciones exigen el grupo `operadores`, verificado contra el claim `cognito:groups` |
| **Repudio** | No se puede saber quién cerró un reporte | `last_actor` en el ítem y log de auditoría estructurado por cada acción sensible |
| **Divulgación** | Fuga de evidencias fotográficas | Bucket totalmente privado, cifrado KMS, acceso solo por URL prefirmada de 5 minutos |
| **Denegación de servicio** | Inundación de reportes automatizados | Throttling en API Gateway (50 rps sostenidos / 100 de ráfaga) y alarma de errores 5xx |
| **Elevación de privilegios** | Una Lambda comprometida accede a todo | Un rol IAM por función con permisos declarados explícitamente; ninguna usa políticas administradas amplias salvo X-Ray |

## 4.2 Autenticación y autorización

La validación del token la ejecuta **API Gateway**, no la aplicación: una petición sin
JWT válido nunca llega a ejecutar código propio. Dentro de la función, la autorización se
resuelve por grupo:

```python
require_group(event, "operadores")   # update_status, indicators
```

Los tokens de acceso duran 60 minutos y el refresh 30 días, con revocación habilitada.
La app móvil es un cliente **público sin secreto** —un secreto embebido en un APK no es
un secreto— y usa SRP, de modo que la contraseña nunca viaja.

## 4.3 Cifrado

| Dato | En tránsito | En reposo |
|---|---|---|
| Peticiones a la API | TLS 1.2+ obligatorio | — |
| Evidencias en S3 | TLS forzado por política de bucket (`aws:SecureTransport`) | SSE-KMS con clave propia, o AES256 de S3 |
| Reportes en DynamoDB | TLS | SSE con clave propia o administrada por AWS |
| Logs en CloudWatch | — | Cifrados |
| Mensajes en SNS/SQS | TLS | KMS (clave propia o `alias/aws/*`) |
| Credenciales en el dispositivo | — | Keychain (iOS) / Keystore (Android) vía Amplify |

**Sobre la clave de cifrado.** Todo dato en reposo está cifrado en ambos modos de
despliegue; lo que decide `use_customer_managed_key` es **quién custodia la clave**. Con
una clave propia se obtienen política de clave, rotación anual auditable y revocación
independiente de AWS —lo que corresponde en producción—; con las claves administradas por
AWS se conserva el cifrado sin el cargo fijo de custodia, que es lo razonable en un
ambiente de desarrollo o en un piloto académico. La justificación completa está en
[ADR-009](05-decisiones-adr.md).

## 4.4 Validación de entrada

Toda entrada se valida en el borde de la función antes de tocar la persistencia:
rango de coordenadas, categoría contra lista blanca, severidad 1–5, longitud de la
descripción, y `evidence_key` sin `..` ni ruta absoluta (path traversal). La URL
prefirmada se emite únicamente para tipos MIME de imagen permitidos y con `ContentLength`
fijado, lo que impide subir un archivo de otro tipo o de tamaño arbitrario.

Los errores no controlados devuelven un 500 genérico con un `request_id`: el detalle
queda en CloudWatch, no en la respuesta. Hay una prueba que verifica exactamente eso
(`test_error_interno_no_filtra_detalle`).

## 4.5 Privacidad de los datos del ciudadano

Un reporte contiene, implícitamente, información sensible: dónde estuvo una persona y a
qué hora. El diseño lo trata como tal.

- **Minimización.** No se solicita nombre, cédula ni teléfono. La única identidad es el
  `sub` opaco de Cognito.
- **Seudonimización en observabilidad.** Los logs registran `sha256(user_id)[:12]`,
  suficiente para correlacionar incidentes, insuficiente para identificar.
- **No exposición.** `user_id` se elimina de toda respuesta de la API.
- **Retención acotada.** TTL de 540 días en DynamoDB y expiración equivalente en S3.
- **Precisión limitada.** Las coordenadas se redondean a 6 decimales; hacia el público
  los datos se exponen agregados en puntos críticos, no como reportes individuales.

## 4.6 Secretos y configuración

No hay credenciales en el repositorio. La app recibe su configuración por
`--dart-define` en tiempo de compilación; las Lambdas, por variables de entorno que
inyecta Terraform; el despliegue en CI usa **OIDC de GitHub Actions** asumiendo un rol de
AWS, sin llaves de acceso de larga vida almacenadas. `.gitignore` excluye `*.tfvars`,
`*.tfstate` y `.env`.

## 4.7 Seguridad en el ciclo de desarrollo

El pipeline de CI ejecuta en cada push y cada pull request:

| Etapa | Herramienta | Qué detecta |
|---|---|---|
| Análisis estático | `ruff` | Errores, imports muertos, antipatrones |
| Seguridad de código | `bandit` | Uso inseguro de APIs, secretos embebidos, aleatoriedad débil |
| Pruebas | `pytest` | 112 casos, incluidos los de validación y fuga de errores |
| Infraestructura | `terraform fmt -check` + `validate` | Deriva de formato y errores de configuración |

## 4.8 Deuda de seguridad reconocida

Ser explícito sobre lo pendiente es parte del rigor:

1. **Sin verificación anti-fraude del reporte.** No se comprueba que la foto se haya
   tomado en el lugar y momento declarados. Mitigación futura: contrastar los metadatos
   EXIF con las coordenadas y la marca de tiempo del servidor.
2. **Sin WAF.** Para exposición pública real convendría AWS WAF delante de la API con
   reglas de reputación y límite por IP.
3. **Rekognition no borra rostros.** Una foto de vía pública puede capturar transeúntes.
   Debería añadirse desenfoque automático de rostros y placas antes de persistir.
4. **La DLQ no tiene reproceso automático.** Hoy hay alarma; falta el consumidor que
   reintente.

---

Anterior: [Modelo de datos](03-modelo-datos.md) ·
Siguiente: [Decisiones de arquitectura](05-decisiones-adr.md)
