output "api_base_url" {
  description = "URL base de la API. Va en la configuración de la app móvil."
  value       = aws_apigatewayv2_stage.main.invoke_url
}

output "cognito_user_pool_id" {
  description = "Identificador del User Pool."
  value       = aws_cognito_user_pool.main.id
}

output "cognito_client_id" {
  description = "Client ID público de la app móvil."
  value       = aws_cognito_user_pool_client.mobile.id
}

output "cognito_domain" {
  description = "Dominio del Hosted UI de Cognito."
  value       = "https://${aws_cognito_user_pool_domain.main.domain}.auth.${var.region}.amazoncognito.com"
}

output "evidence_bucket" {
  description = "Bucket de evidencias fotográficas."
  value       = aws_s3_bucket.evidence.bucket
}

output "dynamodb_table" {
  description = "Tabla de reportes."
  value       = aws_dynamodb_table.reports.name
}

output "dashboard_url" {
  description = "Tablero de CloudWatch."
  value       = "https://${var.region}.console.aws.amazon.com/cloudwatch/home?region=${var.region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "mobile_env" {
  description = "Bloque listo para pegar en mobile/.env"
  value       = <<-EOT
    API_BASE_URL=${aws_apigatewayv2_stage.main.invoke_url}
    COGNITO_USER_POOL_ID=${aws_cognito_user_pool.main.id}
    COGNITO_CLIENT_ID=${aws_cognito_user_pool_client.mobile.id}
    AWS_REGION=${var.region}
  EOT
}
