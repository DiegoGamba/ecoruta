# 8. Guía de despliegue

## 8.1 Requisitos

| Herramienta | Versión mínima | Verificación |
|---|---|---|
| AWS CLI | 2.x, con credenciales configuradas | `aws sts get-caller-identity` |
| Terraform | 1.6 | `terraform version` |
| Python | 3.12 | `python3 --version` |
| Flutter | 3.22 | `flutter doctor` |

Permisos de AWS necesarios: creación de Lambda, API Gateway, DynamoDB, S3, Cognito, IAM,
KMS, EventBridge, SNS, SQS y CloudWatch.

## 8.2 Paso 0 — Estado remoto de Terraform (una sola vez por cuenta)

Terraform guarda su estado en S3 con bloqueo, para que dos despliegues concurrentes no
lo corrompan. Ese bucket debe existir antes del primer `init`:

```bash
export AWS_REGION=us-east-1
export TF_BUCKET="ecoruta-tfstate-$(aws sts get-caller-identity --query Account --output text)"

aws s3api create-bucket --bucket "$TF_BUCKET" --region "$AWS_REGION"
aws s3api put-bucket-versioning --bucket "$TF_BUCKET" \
  --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket "$TF_BUCKET" \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
aws s3api put-public-access-block --bucket "$TF_BUCKET" \
  --public-access-block-configuration \
  'BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true'
```

## 8.3 Paso 1 — Desplegar la infraestructura

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars   # ajuste stage, región y alert_email

terraform init \
  -backend-config="bucket=$TF_BUCKET" \
  -backend-config="key=ecoruta/dev/terraform.tfstate" \
  -backend-config="region=$AWS_REGION" \
  -backend-config="use_lockfile=true"

terraform plan -out=tfplan     # revise el plan antes de aplicar
terraform apply tfplan
```

El empaquetado de las Lambdas es automático: el proveedor `archive` comprime
`backend/src/` y `source_code_hash` fuerza el redespliegue solo cuando el código cambia.

Al terminar, Terraform imprime lo que necesita la app:

```bash
terraform output -raw mobile_env > ../mobile/.env
terraform output api_base_url
terraform output dashboard_url
```

## 8.4 Paso 2 — Crear el grupo de operadores y un usuario de prueba

```bash
POOL=$(terraform output -raw cognito_user_pool_id)

aws cognito-idp admin-create-user \
  --user-pool-id "$POOL" \
  --username operador@ejemplo.co \
  --user-attributes Name=email,Value=operador@ejemplo.co Name=email_verified,Value=true

aws cognito-idp admin-add-user-to-group \
  --user-pool-id "$POOL" \
  --username operador@ejemplo.co \
  --group-name operadores
```

Los ciudadanos se registran por sí mismos desde la app y quedan sin grupo, lo que les
otorga únicamente permisos de creación y consulta.

## 8.5 Paso 3 — Ejecutar la app

Las variables se inyectan en tiempo de compilación; ningún identificador de entorno queda
versionado.

```bash
cd ../mobile
flutter pub get

flutter run \
  --dart-define=API_BASE_URL=$(cd ../infra && terraform output -raw api_base_url) \
  --dart-define=COGNITO_USER_POOL_ID=$(cd ../infra && terraform output -raw cognito_user_pool_id) \
  --dart-define=COGNITO_CLIENT_ID=$(cd ../infra && terraform output -raw cognito_client_id) \
  --dart-define=AWS_REGION=us-east-1
```

Compilación de release:

```bash
flutter build apk --release --dart-define=API_BASE_URL=... --dart-define=...
flutter build ipa  --release --dart-define=API_BASE_URL=... --dart-define=...
```

## 8.6 Paso 4 — Verificar el despliegue

```bash
API=$(cd infra && terraform output -raw api_base_url)

# Sin token debe responder 401: el borde rechaza antes de invocar código propio.
curl -i "$API/puntos-criticos?lat=4.71&lon=-74.07"

# Con token de un usuario autenticado:
TOKEN="<access_token de Cognito>"
curl -X POST "$API/reportes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lat":4.710989,"lon":-74.072092,"category":"escombros","severity":4,
       "description":"prueba de despliegue"}'
```

El archivo [`backend/api.http`](../backend/api.http) tiene el flujo completo listo para
ejecutar desde VS Code o IntelliJ.

## 8.7 Pruebas y calidad locales

```bash
cd backend
pip install -r requirements-dev.txt
pytest --cov=src            # 109 pruebas
ruff check .
bandit -r src/

cd ../infra
terraform fmt -check -recursive
terraform validate

cd ../mobile
flutter analyze
flutter test
```

## 8.8 Despliegue continuo

El flujo de trabajo [`ci.yml`](../.github/workflows/ci.yml) ejecuta pruebas, linting,
análisis de seguridad y validación de Terraform en cada push y pull request.
[`deploy.yml`](../.github/workflows/deploy.yml) aplica la infraestructura al fusionar en
`main`, autenticándose contra AWS por **OIDC** —sin llaves de acceso guardadas en GitHub—.
Requiere configurar en el repositorio la variable `AWS_ROLE_ARN` y el rol de confianza
correspondiente en IAM.

## 8.9 Destruir el entorno

```bash
cd infra
terraform destroy
```

El bucket de evidencias tiene versionado activo; si contiene objetos, vacíelo antes:

```bash
aws s3 rm "s3://$(terraform output -raw evidence_bucket)" --recursive
```

## 8.10 Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `401 Unauthorized` en toda la API | Token vencido (60 min) o del pool equivocado | Reautenticar; verificar `COGNITO_CLIENT_ID` |
| `403` al cambiar estado | El usuario no está en `operadores` | `admin-add-user-to-group` (§8.4) |
| La app arranca con "Faltan variables de compilación" | Se ejecutó sin `--dart-define` | Usar el comando de §8.5 |
| `BucketAlreadyExists` en el `apply` | El nombre de bucket es global en AWS | Cambiar `project` en `terraform.tfvars` |
| La foto sube pero no se clasifica | La notificación de S3 requiere la Lambda creada | Reintentar `terraform apply`; verificar el log de `classify_evidence` |

---

Anterior: [Proyección investigativa](07-proyeccion-investigativa.md) ·
Siguiente: [Referencia de la API](09-api.md)
