##############################################################################
# Capa de datos: DynamoDB single-table + KMS
##############################################################################

data "aws_caller_identity" "current" {}

resource "aws_kms_key" "main" {
  description             = "Clave de cifrado de EcoRuta (${var.stage})"
  enable_key_rotation     = true
  deletion_window_in_days = local.is_prod ? 30 : 7
}

resource "aws_kms_alias" "main" {
  name          = "alias/${local.name}"
  target_key_id = aws_kms_key.main.key_id
}

# Diseño single-table: una sola tabla con claves genéricas PK/SK y tres GSI.
# Ventaja: cada consulta del caso de uso se resuelve con un Query (nunca Scan),
# a costo y latencia constantes.
resource "aws_dynamodb_table" "reports" {
  name         = "${local.name}-reportes"
  billing_mode = "PAY_PER_REQUEST" # sin capacidad ociosa: se paga por uso real
  hash_key     = "PK"
  range_key    = "SK"

  attribute {
    name = "PK"
    type = "S"
  }
  attribute {
    name = "SK"
    type = "S"
  }
  attribute {
    name = "GSI1PK" # GEO#<geohash6>  -> reportes por zona
    type = "S"
  }
  attribute {
    name = "GSI1SK"
    type = "S"
  }
  attribute {
    name = "GSI2PK" # STATUS#<estado> -> bandeja operativa
    type = "S"
  }
  attribute {
    name = "GSI2SK"
    type = "S"
  }
  attribute {
    name = "GSI3PK" # EVID#<key>      -> resolver reporte desde la evidencia
    type = "S"
  }
  attribute {
    name = "GSI3SK"
    type = "S"
  }

  global_secondary_index {
    name            = "GSI1"
    hash_key        = "GSI1PK"
    range_key       = "GSI1SK"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "GSI2"
    hash_key        = "GSI2PK"
    range_key       = "GSI2SK"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "GSI3"
    hash_key        = "GSI3PK"
    range_key       = "GSI3SK"
    projection_type = "KEYS_ONLY"
  }

  # Minimización de datos: los reportes expiran automáticamente a los 540 días.
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = var.enable_point_in_time_recovery
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.main.arn
  }

  lifecycle {
    prevent_destroy = false # cambiar a true en prod
  }
}
