output "raw_bucket_name" {
  description = "Name of the raw data bucket"
  value       = aws_s3_bucket.raw_bucket.bucket
}

output "processed_bucket_name" {
  description = "Name of the processed data bucket"
  value       = aws_s3_bucket.processed_bucket.bucket
}

output "curated_bucket_name" {
  description = "Name of the curated data bucket"
  value       = aws_s3_bucket.curated_bucket.bucket
}

output "raw_bucket_arn" {
  description = "ARN of the raw data bucket"
  value       = aws_s3_bucket.raw_bucket.arn
}

output "processed_bucket_arn" {
  description = "ARN of the processed data bucket"
  value       = aws_s3_bucket.processed_bucket.arn
}

output "curated_bucket_arn" {
  description = "ARN of the curated data bucket"
  value       = aws_s3_bucket.curated_bucket.arn
}
