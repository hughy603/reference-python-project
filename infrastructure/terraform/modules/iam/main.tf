terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0.0"
    }
  }
}

# Data Engineer Role
resource "aws_iam_role" "data_engineer_role" {
  name = "${var.organization_name}_data_engineer_${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Role        = "DataEngineer"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}

# Data Engineer Policy
resource "aws_iam_policy" "data_engineer_policy" {
  name        = "${var.organization_name}_data_engineer_policy_${var.environment}"
  description = "Policy for data engineers to manage data lake resources"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ]
        Resource = [
          var.raw_bucket_arn,
          "${var.raw_bucket_arn}/*",
          var.processed_bucket_arn,
          "${var.processed_bucket_arn}/*",
          var.curated_bucket_arn,
          "${var.curated_bucket_arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "glue:*Database*",
          "glue:*Table*",
          "glue:*Partition*",
          "glue:*UserDefinedFunction*",
          "glue:*Job*",
          "glue:*Crawler*"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "athena:StartQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults",
          "athena:StopQueryExecution",
          "athena:GetWorkGroup",
          "athena:ListWorkGroups"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Role        = "DataEngineer"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}

# Attach policy to data engineer role
resource "aws_iam_role_policy_attachment" "data_engineer_policy_attachment" {
  role       = aws_iam_role.data_engineer_role.name
  policy_arn = aws_iam_policy.data_engineer_policy.arn
}

# Data Scientist Role
resource "aws_iam_role" "data_scientist_role" {
  name = "${var.organization_name}_data_scientist_${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Role        = "DataScientist"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}

# Data Scientist Policy
resource "aws_iam_policy" "data_scientist_policy" {
  name        = "${var.organization_name}_data_scientist_policy_${var.environment}"
  description = "Policy for data scientists to access processed and curated data"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          var.processed_bucket_arn,
          "${var.processed_bucket_arn}/*",
          var.curated_bucket_arn,
          "${var.curated_bucket_arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject"
        ]
        Resource = [
          var.curated_bucket_arn,
          "${var.curated_bucket_arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "glue:GetDatabase",
          "glue:GetDatabases",
          "glue:GetTable",
          "glue:GetTables",
          "glue:GetPartition",
          "glue:GetPartitions",
          "glue:BatchGetPartition"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "athena:StartQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults",
          "athena:StopQueryExecution",
          "athena:GetWorkGroup"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Role        = "DataScientist"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}

# Attach policy to data scientist role
resource "aws_iam_role_policy_attachment" "data_scientist_policy_attachment" {
  role       = aws_iam_role.data_scientist_role.name
  policy_arn = aws_iam_policy.data_scientist_policy.arn
}

# Data Analyst Role
resource "aws_iam_role" "data_analyst_role" {
  name = "${var.organization_name}_data_analyst_${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Role        = "DataAnalyst"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}

# Data Analyst Policy
resource "aws_iam_policy" "data_analyst_policy" {
  name        = "${var.organization_name}_data_analyst_policy_${var.environment}"
  description = "Policy for data analysts to access curated data"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          var.curated_bucket_arn,
          "${var.curated_bucket_arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "glue:GetDatabase",
          "glue:GetDatabases",
          "glue:GetTable",
          "glue:GetTables",
          "glue:GetPartition",
          "glue:GetPartitions"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "athena:StartQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults",
          "athena:StopQueryExecution"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Role        = "DataAnalyst"
    Environment = var.environment
    Project     = var.project_name
    Owner       = var.owner
  }
}

# Attach policy to data analyst role
resource "aws_iam_role_policy_attachment" "data_analyst_policy_attachment" {
  role       = aws_iam_role.data_analyst_role.name
  policy_arn = aws_iam_policy.data_analyst_policy.arn
}
