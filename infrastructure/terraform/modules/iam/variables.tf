variable "organization_name" {
  description = "Organization name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., dev, test, prod)"
  type        = string
}

variable "project_name" {
  description = "Project name for resource tagging"
  type        = string
  default     = "EnterpriseDataEngineering"
}

variable "owner" {
  description = "Owner name for resource tagging"
  type        = string
  default     = "DataEngineering"
}

variable "raw_bucket_arn" {
  description = "ARN of the raw data bucket"
  type        = string
}

variable "processed_bucket_arn" {
  description = "ARN of the processed data bucket"
  type        = string
}

variable "curated_bucket_arn" {
  description = "ARN of the curated data bucket"
  type        = string
}
