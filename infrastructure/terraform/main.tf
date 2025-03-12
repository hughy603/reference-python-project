terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }

  backend "s3" {
    # These values must be provided via backend configuration
    # bucket         = "terraform-state-bucket"
    # key            = "enterprise-data-engineering/terraform.tfstate"
    # region         = "us-east-1"
    # dynamodb_table = "terraform-locks"
    # encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = "EnterpriseDataEngineering"
      ManagedBy   = "Terraform"
      Owner       = "DataEngineeringTeam"
    }
  }
}

# Variables
variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (e.g., dev, test, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "Environment must be one of: dev, test, prod."
  }
}

variable "organization_name" {
  description = "Organization name for resource naming"
  type        = string
  default     = "enterprise"
}

variable "data_lake_name" {
  description = "Name of the data lake"
  type        = string
  default     = "datalake"
}

variable "retention_days" {
  description = "Number of days to retain data in the data lake"
  type        = number
  default     = 365
}

# Data Lake S3 Buckets
module "data_lake_buckets" {
  source = "./modules/data_lake"

  organization_name = var.organization_name
  data_lake_name    = var.data_lake_name
  environment       = var.environment
  retention_days    = var.retention_days
  prefix            = "${var.organization_name}-${var.environment}"
}

# Glue Catalog Database
resource "aws_glue_catalog_database" "data_catalog" {
  name        = "${var.organization_name}_${var.data_lake_name}_${var.environment}"
  description = "Glue catalog database for ${var.data_lake_name} data lake"
}

# IAM Roles for Data Engineering
module "data_engineering_iam" {
  source = "./modules/iam"

  organization_name    = var.organization_name
  environment          = var.environment
  raw_bucket_arn       = module.data_lake_buckets.raw_bucket_arn
  processed_bucket_arn = module.data_lake_buckets.processed_bucket_arn
  curated_bucket_arn   = module.data_lake_buckets.curated_bucket_arn
}

# Outputs
output "raw_bucket_name" {
  description = "Name of the raw data bucket"
  value       = module.data_lake_buckets.raw_bucket_name
}

output "processed_bucket_name" {
  description = "Name of the processed data bucket"
  value       = module.data_lake_buckets.processed_bucket_name
}

output "curated_bucket_name" {
  description = "Name of the curated data bucket"
  value       = module.data_lake_buckets.curated_bucket_name
}

output "glue_database_name" {
  description = "Name of the Glue catalog database"
  value       = aws_glue_catalog_database.data_catalog.name
}

output "data_engineer_role_arn" {
  description = "ARN of the data engineer IAM role"
  value       = module.data_engineering_iam.data_engineer_role_arn
}
