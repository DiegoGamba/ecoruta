# Infraestructura EcoRuta

Terraform 1.6 · proveedor AWS 5.x. Ningún recurso se crea a mano.

| Archivo | Contenido |
|---|---|
| `versions.tf` | Versiones, backend remoto S3 y etiquetas por defecto |
| `variables.tf` | Variables con validación y locales compartidos |
| `data.tf` | Tabla DynamoDB single-table con 3 GSI, TTL, PITR y clave KMS |
| `storage.tf` | Bucket de evidencias: cifrado, ciclo de vida, TLS obligatorio, notificación |
| `auth.tf` | Cognito: user pool, cliente móvil público, grupos `ciudadanos` y `operadores` |
| `compute.tf` | Ocho Lambdas con `for_each` y un rol IAM de mínimo privilegio por función |
| `api.tf` | API Gateway HTTP, autorizador JWT, rutas, throttling y logs de acceso |
| `events.tf` | EventBridge, SNS y cola de mensajes fallidos |
| `monitoring.tf` | Alarmas por función, API, DynamoDB y DLQ, más tablero operativo |
| `outputs.tf` | Salidas, incluida `mobile_env` lista para la app |

## Cómo se declaran los permisos

`compute.tf` define un mapa `functions` donde cada entrada lista los permisos que necesita:

```hcl
create_report = {
  handler = "src.handlers.create_report.handler"
  perms   = ["ddb_write", "events_put"]
}
```

Terraform materializa esos permisos desde `policy_statements`. Agregar una función es
agregar una entrada al mapa; nadie puede otorgarle acceso a algo sin declararlo.

## Uso

Ver la guía completa en [`../docs/08-despliegue.md`](../docs/08-despliegue.md).

```bash
terraform init -backend-config="bucket=$TF_BUCKET" \
               -backend-config="key=ecoruta/dev/terraform.tfstate" \
               -backend-config="region=us-east-1"
terraform plan -out=tfplan
terraform apply tfplan
```
