##############################################################################
# Identidad: Cognito User Pool (ciudadanos y operadores)
##############################################################################

resource "aws_cognito_user_pool" "main" {
  name = "${local.name}-usuarios"

  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]
  mfa_configuration        = "OPTIONAL"

  software_token_mfa_configuration {
    enabled = true
  }

  password_policy {
    minimum_length                   = 12
    require_lowercase                = true
    require_uppercase                = true
    require_numbers                  = true
    require_symbols                  = true
    temporary_password_validity_days = 3
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  # Defensa contra credenciales filtradas y accesos anómalos.
  user_pool_add_ons {
    advanced_security_mode = "AUDIT"
  }

  admin_create_user_config {
    allow_admin_create_user_only = false
  }

  deletion_protection = local.is_prod ? "ACTIVE" : "INACTIVE"
}

resource "aws_cognito_user_pool_domain" "main" {
  domain       = "${local.name}-${data.aws_caller_identity.current.account_id}"
  user_pool_id = aws_cognito_user_pool.main.id
}

# La app móvil es un cliente público: sin secreto, con PKCE y tokens cortos.
resource "aws_cognito_user_pool_client" "mobile" {
  name         = "${local.name}-app-movil"
  user_pool_id = aws_cognito_user_pool.main.id

  generate_secret               = false
  prevent_user_existence_errors = "ENABLED"
  enable_token_revocation       = true

  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
  ]

  access_token_validity  = 60 # minutos
  id_token_validity      = 60
  refresh_token_validity = 30 # días

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  supported_identity_providers         = ["COGNITO"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email", "profile"]
  callback_urls                        = ["ecoruta://callback"]
  logout_urls                          = ["ecoruta://logout"]
}

# Autorización por grupos: el claim `cognito:groups` llega en el JWT y las
# Lambdas lo verifican (`require_group`).
resource "aws_cognito_user_group" "ciudadanos" {
  name         = "ciudadanos"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Usuarios que crean y consultan reportes."
  precedence   = 10
}

resource "aws_cognito_user_group" "operadores" {
  name         = "operadores"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Personal de la entidad de aseo: cambia estados y ve indicadores."
  precedence   = 1
}
