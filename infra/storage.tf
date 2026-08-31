##############################################################################
# Almacenamiento de evidencias fotográficas
##############################################################################

resource "aws_s3_bucket" "evidence" {
  bucket = "${local.name}-evidencias-${data.aws_caller_identity.current.account_id}"
}

# Todo acceso público queda bloqueado: la app usa URLs prefirmadas de vida corta.
resource "aws_s3_bucket_public_access_block" "evidence" {
  bucket                  = aws_s3_bucket.evidence.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.main.arn
    }
    bucket_key_enabled = true # reduce el costo de llamadas a KMS
  }
}

resource "aws_s3_bucket_versioning" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Ciclo de vida alineado con la retención del reporte en DynamoDB.
resource "aws_s3_bucket_lifecycle_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id

  rule {
    id     = "archivar-y-expirar"
    status = "Enabled"

    filter {
      prefix = "evidencias/"
    }

    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 180
      storage_class = "GLACIER_IR"
    }

    expiration {
      days = 540
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }

  rule {
    id     = "limpiar-multipart-incompletos"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT"]
    allowed_origins = var.cors_allowed_origins
    max_age_seconds = 3000
  }
}

# Se exige TLS para cualquier operación sobre el bucket.
resource "aws_s3_bucket_policy" "evidence_tls_only" {
  bucket = aws_s3_bucket.evidence.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "DenegarTransportePlano"
      Effect    = "Deny"
      Principal = "*"
      Action    = "s3:*"
      Resource = [
        aws_s3_bucket.evidence.arn,
        "${aws_s3_bucket.evidence.arn}/*",
      ]
      Condition = {
        Bool = { "aws:SecureTransport" = "false" }
      }
    }]
  })
}

# Cada foto nueva dispara la clasificación asistida.
resource "aws_s3_bucket_notification" "evidence" {
  bucket = aws_s3_bucket.evidence.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.fn["classify_evidence"].arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "evidencias/"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fn["classify_evidence"].function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.evidence.arn
}
