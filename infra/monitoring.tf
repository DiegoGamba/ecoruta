##############################################################################
# Observabilidad: alarmas y tablero operativo
##############################################################################

resource "aws_cloudwatch_metric_alarm" "fn_errors" {
  for_each = local.functions

  alarm_name          = "${local.name}-${each.key}-errores"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 3
  treat_missing_data  = "notBreaching"
  alarm_description   = "Más de 3 errores en 5 minutos en ${each.key}"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    FunctionName = aws_lambda_function.fn[each.key].function_name
  }
}

resource "aws_cloudwatch_metric_alarm" "api_5xx" {
  alarm_name          = "${local.name}-api-5xx"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "5xx"
  namespace           = "AWS/ApiGateway"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ApiId = aws_apigatewayv2_api.main.id
  }
}

resource "aws_cloudwatch_metric_alarm" "ddb_throttle" {
  alarm_name          = "${local.name}-ddb-throttle"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ThrottledRequests"
  namespace           = "AWS/DynamoDB"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    TableName = aws_dynamodb_table.reports.name
  }
}

# Mensajes en la DLQ = eventos perdidos: siempre debe estar en cero.
resource "aws_cloudwatch_metric_alarm" "dlq_no_vacia" {
  alarm_name          = "${local.name}-dlq-con-mensajes"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Maximum"
  threshold           = 0
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    QueueName = aws_sqs_queue.dlq.name
  }
}

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${local.name}-operacion"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          title  = "API - peticiones y latencia"
          region = var.region
          metrics = [
            ["AWS/ApiGateway", "Count", "ApiId", aws_apigatewayv2_api.main.id],
            [".", "Latency", ".", ".", { stat = "p95" }],
            [".", "4xx", ".", "."],
            [".", "5xx", ".", "."],
          ]
          period = 300
        }
      },
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          title  = "Lambda - invocaciones, errores y duración"
          region = var.region
          metrics = [
            for k, _ in local.functions :
            ["AWS/Lambda", "Errors", "FunctionName", "${local.name}-${k}"]
          ]
          period = 300
        }
      },
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          title  = "DynamoDB - capacidad consumida"
          region = var.region
          metrics = [
            ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", aws_dynamodb_table.reports.name],
            [".", "ConsumedWriteCapacityUnits", ".", "."],
          ]
          period = 300
        }
      },
    ]
  })
}
