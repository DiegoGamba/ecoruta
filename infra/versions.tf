terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }

  # Estado remoto con bloqueo: evita que dos despliegues concurrentes
  # corrompan el estado. Se inicializa con `terraform init -backend-config=...`.
  backend "s3" {}
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = "EcoRuta"
      Environment = var.stage
      ManagedBy   = "Terraform"
      Course      = "DAM1-Diseno-Aplicaciones-Moviles"
    }
  }
}
