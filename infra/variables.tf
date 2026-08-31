variable "project" {
  description = "Prefijo de nombres para todos los recursos."
  type        = string
  default     = "ecoruta"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,20}$", var.project))
    error_message = "El prefijo debe ser minúsculas, números o guiones (3-21 caracteres)."
  }
}

variable "stage" {
  description = "Ambiente de despliegue."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "qa", "prod"], var.stage)
    error_message = "stage debe ser dev, qa o prod."
  }
}

variable "region" {
  description = "Región de AWS."
  type        = string
  default     = "us-east-1"
}

variable "log_retention_days" {
  description = "Retención de logs en CloudWatch."
  type        = number
  default     = 30
}

variable "lambda_memory_mb" {
  description = "Memoria asignada a las Lambdas de la API."
  type        = number
  default     = 512
}

variable "lambda_timeout_s" {
  description = "Timeout de las Lambdas de la API."
  type        = number
  default     = 15
}

variable "alert_email" {
  description = "Correo del operador de aseo que recibe alertas prioritarias. Vacío = sin suscripción."
  type        = string
  default     = ""
}

variable "cors_allowed_origins" {
  description = "Orígenes permitidos por CORS en el panel web."
  type        = list(string)
  default     = ["http://localhost:5173"]
}

variable "enable_point_in_time_recovery" {
  description = "Backup continuo de DynamoDB (recomendado en prod)."
  type        = bool
  default     = true
}

variable "api_burst_limit" {
  description = "Ráfaga máxima de peticiones por segundo en la API."
  type        = number
  default     = 100
}

variable "api_rate_limit" {
  description = "Peticiones por segundo sostenidas en la API."
  type        = number
  default     = 50
}

variable "use_customer_managed_key" {
  description = <<-EOT
    Clave KMS propia (CMK) para cifrar datos en reposo.

    true  → control total: política de clave propia, rotación anual auditable y
            revocación independiente de AWS. Cuesta 1 USD/mes por clave.
    false → claves administradas por AWS (o cifrado propio de S3). El dato sigue
            cifrado en reposo, sin costo fijo. Es la opción adecuada para el
            piloto académico y para cualquier ambiente de desarrollo.

    Recomendado: false en dev/qa, true en prod.
  EOT
  type        = bool
  default     = false
}

locals {
  name    = "${var.project}-${var.stage}"
  is_prod = var.stage == "prod"

  # ARN de la clave propia, o null cuando se usan las claves de AWS.
  # Los recursos consultan este valor en vez de referenciar la clave directamente.
  kms_arn = var.use_customer_managed_key ? aws_kms_key.main[0].arn : null

  # Algoritmo de cifrado del bucket de evidencias. Debe coincidir con la
  # cabecera que la app envía al subir la foto, así que viaja hasta el cliente.
  evidence_sse = var.use_customer_managed_key ? "aws:kms" : "AES256"
}
