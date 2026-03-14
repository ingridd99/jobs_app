terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      # Where to download the provider from.
      # "hashicorp/aws" means: from HashiCorp's registry, the AWS plugin.
      # (like "pip install boto3" but for Terraform)
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}