terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.9.0"
    }
  }
}

locals {
  raw_bucket_name       = var.raw_bucket_name != null ? var.raw_bucket_name : "${var.organization_name}-${var.data_lake_name}-raw-${var.environment}"
  processed_bucket_name = var.processed_bucket_name != null ? var.processed_bucket_name : "${var.organization_name}-${var.data_lake_name}-processed-${var.environment}"
  curated_bucket_name   = var.curated_bucket_name != null ? var.curated_bucket_name : "${var.organization_name}-${var.data_lake_name}-curated-${var.environment}"
  common_tags = {
    Environment = var.environment
    Project     = var.data_lake_name
    Owner       = "DataEngineering"
    ManagedBy   = "Terraform"
  }
}

# Raw data bucket
resource "aws_s3_bucket" "raw_bucket" {
  bucket = local.raw_bucket_name

  tags = merge(
    var.tags,
    local.common_tags,
    {
      Name  = "${var.prefix}-raw-bucket"
      Layer = "raw"
    }
  )
}

# Processed data bucket
resource "aws_s3_bucket" "processed_bucket" {
  bucket = local.processed_bucket_name

  tags = merge(
    var.tags,
    local.common_tags,
    {
      Name  = "${var.prefix}-processed-bucket"
      Layer = "processed"
    }
  )
}

# Curated data bucket
resource "aws_s3_bucket" "curated_bucket" {
  bucket = local.curated_bucket_name

  tags = merge(
    var.tags,
    local.common_tags,
    {
      Name  = "${var.prefix}-curated-bucket"
      Layer = "curated"
    }
  )
}

# Lifecycle policy for raw data
resource "aws_s3_bucket_lifecycle_configuration" "raw_bucket_lifecycle" {
  bucket = aws_s3_bucket.raw_bucket.id

  rule {
    id     = "archive-after-retention-period"
    status = "Enabled"

    filter {
      prefix = ""
    }

    transition {
      days          = var.retention_days
      storage_class = "GLACIER"
    }

    expiration {
      days = var.retention_days * 2
    }
  }
}

# Server-side encryption for raw bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "raw_bucket_encryption" {
  bucket = aws_s3_bucket.raw_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Server-side encryption for processed bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "processed_bucket_encryption" {
  bucket = aws_s3_bucket.processed_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Server-side encryption for curated bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "curated_bucket_encryption" {
  bucket = aws_s3_bucket.curated_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Public access block for all buckets
resource "aws_s3_bucket_public_access_block" "raw_bucket_access" {
  bucket = aws_s3_bucket.raw_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "processed_bucket_access" {
  bucket = aws_s3_bucket.processed_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "curated_bucket_access" {
  bucket = aws_s3_bucket.curated_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
