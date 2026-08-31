##############################################################################
# Mensajería asíncrona: EventBridge + SNS + colas de mensajes fallidos
##############################################################################

resource "aws_cloudwatch_event_bus" "main" {
  name = "${local.name}-bus"
}

# Desacople: la Lambda que crea el reporte solo publica un evento; quién
# reacciona (alertas, futuras integraciones) se agrega sin tocar ese código.
resource "aws_cloudwatch_event_rule" "reporte_creado" {
  name           = "${local.name}-reporte-creado"
  event_bus_name = aws_cloudwatch_event_bus.main.name
  description    = "Reportes nuevos que deben evaluarse para alerta prioritaria"

  event_pattern = jsonencode({
    source        = ["ecoruta.api"]
    "detail-type" = ["ReporteCreado"]
  })
}

resource "aws_cloudwatch_event_target" "notificar" {
  rule           = aws_cloudwatch_event_rule.reporte_creado.name
  event_bus_name = aws_cloudwatch_event_bus.main.name
  arn            = aws_lambda_function.fn["notify_operator"].arn

  retry_policy {
    maximum_retry_attempts       = 3
    maximum_event_age_in_seconds = 3600
  }

  dead_letter_config {
    arn = aws_sqs_queue.dlq.arn
  }
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fn["notify_operator"].function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.reporte_creado.arn
}

# Ningún evento se pierde en silencio: lo que falla tras los reintentos queda
# en la DLQ para inspección y reproceso.
resource "aws_sqs_queue" "dlq" {
  name                      = "${local.name}-dlq"
  message_retention_seconds = 1209600 # 14 días
  # alias/aws/sqs es la clave administrada por AWS: cifra sin costo de custodia.
  kms_master_key_id = var.use_customer_managed_key ? local.kms_arn : "alias/aws/sqs"
}

resource "aws_sqs_queue_policy" "dlq" {
  queue_url = aws_sqs_queue.dlq.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "events.amazonaws.com" }
      Action    = "sqs:SendMessage"
      Resource  = aws_sqs_queue.dlq.arn
      Condition = {
        ArnEquals = { "aws:SourceArn" = aws_cloudwatch_event_rule.reporte_creado.arn }
      }
    }]
  })
}

resource "aws_sns_topic" "alerts" {
  name              = "${local.name}-alertas"
  kms_master_key_id = var.use_customer_managed_key ? local.kms_arn : "alias/aws/sns"
}

resource "aws_sns_topic_subscription" "operador" {
  count     = var.alert_email == "" ? 0 : 1
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}
