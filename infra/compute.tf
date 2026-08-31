##############################################################################
# Cómputo: Lambdas (una por caso de uso) con permisos de mínimo privilegio
##############################################################################

locals {
  # Una función por caso de uso: fallos aislados, permisos finos y métricas
  # por endpoint. `perms` declara únicamente lo que cada función necesita.
  functions = {
    create_report = {
      handler = "src.handlers.create_report.handler"
      perms   = ["ddb_write", "events_put"]
    }
    get_report = {
      handler = "src.handlers.get_report.handler"
      perms   = ["ddb_read"]
    }
    update_status = {
      handler = "src.handlers.update_status.handler"
      perms   = ["ddb_read", "ddb_write", "events_put"]
    }
    hotspots = {
      handler = "src.handlers.hotspots.handler"
      perms   = ["ddb_read"]
    }
    indicators = {
      handler = "src.handlers.indicators.handler"
      perms   = ["ddb_read"]
    }
    presign_evidence = {
      handler = "src.handlers.presign_evidence.handler"
      perms   = ["s3_put"]
    }
    classify_evidence = {
      handler = "src.handlers.classify_evidence.handler"
      perms   = ["ddb_read", "ddb_write", "s3_get", "rekognition"]
    }
    notify_operator = {
      handler = "src.handlers.notify_operator.handler"
      perms   = ["sns_publish"]
    }
  }

  policy_statements = {
    ddb_read = {
      actions = ["dynamodb:GetItem", "dynamodb:Query", "dynamodb:BatchGetItem"]
      resources = [
        aws_dynamodb_table.reports.arn,
        "${aws_dynamodb_table.reports.arn}/index/*",
      ]
    }
    ddb_write = {
      actions   = ["dynamodb:PutItem", "dynamodb:UpdateItem"]
      resources = [aws_dynamodb_table.reports.arn]
    }
    s3_put = {
      actions   = ["s3:PutObject"]
      resources = ["${aws_s3_bucket.evidence.arn}/evidencias/*"]
    }
    s3_get = {
      actions   = ["s3:GetObject"]
      resources = ["${aws_s3_bucket.evidence.arn}/evidencias/*"]
    }
    events_put = {
      actions   = ["events:PutEvents"]
      resources = [aws_cloudwatch_event_bus.main.arn]
    }
    sns_publish = {
      actions   = ["sns:Publish"]
      resources = [aws_sns_topic.alerts.arn]
    }
    rekognition = {
      actions   = ["rekognition:DetectLabels"]
      resources = ["*"] # Rekognition no admite ARN de recurso para esta acción
    }
  }
}

data "archive_file" "backend" {
  type        = "zip"
  source_dir  = "${path.module}/../backend/src"
  output_path = "${path.module}/.build/backend.zip"
  excludes    = ["**/__pycache__/**", "**/*.pyc"]
}

resource "aws_cloudwatch_log_group" "fn" {
  for_each          = local.functions
  name              = "/aws/lambda/${local.name}-${each.key}"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.main.arn
}

resource "aws_iam_role" "fn" {
  for_each = local.functions
  name     = "${local.name}-${each.key}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

# Permisos de escritura de logs, acotados al log group propio de cada función.
resource "aws_iam_role_policy" "fn_logs" {
  for_each = local.functions
  name     = "logs"
  role     = aws_iam_role.fn[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["logs:CreateLogStream", "logs:PutLogEvents"]
      Resource = "${aws_cloudwatch_log_group.fn[each.key].arn}:*"
    }]
  })
}

resource "aws_iam_role_policy" "fn_scoped" {
  for_each = local.functions
  name     = "acceso-recursos"
  role     = aws_iam_role.fn[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat(
      [for p in each.value.perms : {
        Effect   = "Allow"
        Action   = local.policy_statements[p].actions
        Resource = local.policy_statements[p].resources
      }],
      [{
        Effect   = "Allow"
        Action   = ["kms:Decrypt", "kms:GenerateDataKey"]
        Resource = aws_kms_key.main.arn
      }]
    )
  })
}

resource "aws_lambda_function" "fn" {
  for_each = local.functions

  function_name    = "${local.name}-${each.key}"
  role             = aws_iam_role.fn[each.key].arn
  handler          = each.value.handler
  runtime          = "python3.12"
  architectures    = ["arm64"] # Graviton: ~20% menos costo por invocación
  filename         = data.archive_file.backend.output_path
  source_code_hash = data.archive_file.backend.output_base64sha256
  memory_size      = var.lambda_memory_mb
  timeout          = each.key == "classify_evidence" ? 60 : var.lambda_timeout_s

  environment {
    variables = {
      TABLE_NAME      = aws_dynamodb_table.reports.name
      EVIDENCE_BUCKET = aws_s3_bucket.evidence.bucket
      EVENT_BUS       = aws_cloudwatch_event_bus.main.name
      ALERT_TOPIC_ARN = aws_sns_topic.alerts.arn
      STAGE           = var.stage
      LOG_LEVEL       = local.is_prod ? "INFO" : "DEBUG"
      CLUSTER_RADIUS_M = "120"
      CLUSTER_MIN_REPORTS = "3"
    }
  }

  tracing_config {
    mode = "Active" # trazas distribuidas en X-Ray
  }

  depends_on = [aws_cloudwatch_log_group.fn]
}

# X-Ray necesita permisos propios.
resource "aws_iam_role_policy_attachment" "fn_xray" {
  for_each   = local.functions
  role       = aws_iam_role.fn[each.key].name
  policy_arn = "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
}
