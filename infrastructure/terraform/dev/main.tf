terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    # These values will be filled by the CI/CD pipeline
    # bucket = "terraform-state-bucket"
    # key    = "dev/terraform.tfstate"
    # region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = "DataEngineering"
      ManagedBy   = "Terraform"
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
  description = "Deployment environment (dev, test, prod)"
  type        = string
  default     = "dev"
}

variable "lambda_package_bucket" {
  description = "S3 bucket containing the Lambda package"
  type        = string
}

variable "lambda_package_version" {
  description = "Version of the Lambda package to deploy"
  type        = string
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.environment}-data-engineering-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = {
    Environment = var.environment
    Project     = "EnterpriseDataEngineering"
    Owner       = "DataEngineering"
  }
}

# Attach policies to Lambda role
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Custom policy for S3 access
resource "aws_iam_policy" "lambda_s3_access" {
  name        = "${var.environment}-lambda-s3-access"
  description = "Allow Lambda to access S3 resources"

  tags = {
    Environment = var.environment
    Project     = "EnterpriseDataEngineering"
    Owner       = "DataEngineering"
  }

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:s3:::${var.lambda_package_bucket}",
          "arn:aws:s3:::${var.lambda_package_bucket}/*",
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_s3_access" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_s3_access.arn
}

# Lambda function
resource "aws_lambda_function" "data_engineering" {
  function_name = "${var.environment}-data-engineering"
  description   = "Lambda function for data engineering tasks"

  s3_bucket = var.lambda_package_bucket
  s3_key    = "${var.environment}/lambda-packages/${var.lambda_package_version}/package.whl"

  runtime     = "python3.11"
  handler     = "lambda_handler.handler"
  memory_size = 512
  timeout     = 300

  role = aws_iam_role.lambda_execution_role.arn

  environment {
    variables = {
      ENV       = var.environment
      LOG_LEVEL = "INFO"
    }
  }

  tags = {
    Environment = var.environment
    Project     = "EnterpriseDataEngineering"
    Owner       = "DataEngineering"
  }
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.data_engineering.function_name}"
  retention_in_days = 30

  tags = {
    Environment = var.environment
    Project     = "EnterpriseDataEngineering"
    Owner       = "DataEngineering"
  }
}

# API Gateway
resource "aws_api_gateway_rest_api" "api" {
  name        = "${var.environment}-data-engineering-api"
  description = "API Gateway for Data Engineering Lambda"

  tags = {
    Environment = var.environment
    Project     = "EnterpriseDataEngineering"
    Owner       = "DataEngineering"
  }
}

resource "aws_api_gateway_resource" "resource" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "process"
}

resource "aws_api_gateway_method" "method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.resource.id
  http_method             = aws_api_gateway_method.method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.data_engineering.invoke_arn
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.data_engineering.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "deployment" {
  depends_on = [
    aws_api_gateway_integration.integration
  ]

  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = var.environment

  lifecycle {
    create_before_destroy = true
  }
}

# Outputs
output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.data_engineering.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.data_engineering.arn
}

output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = "${aws_api_gateway_deployment.deployment.invoke_url}${aws_api_gateway_resource.resource.path}"
}
