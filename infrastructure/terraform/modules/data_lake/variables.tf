variable "organization_name" {
  description = "Organization name for resource naming"
  type        = string
}

variable "data_lake_name" {
  description = "Name of the data lake"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "retention_days" {
  description = "Number of days to retain data in the data lake"
  type        = number
  default     = 365
}

variable "prefix" {
  description = "Prefix to be used in resource names"
  type        = string
}

variable "raw_bucket_name" {
  description = "Name for the raw data bucket"
  type        = string
  default     = null
}

variable "processed_bucket_name" {
  description = "Name for the processed data bucket"
  type        = string
  default     = null
}

variable "curated_bucket_name" {
  description = "Name for the curated data bucket"
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
