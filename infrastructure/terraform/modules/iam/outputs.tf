output "data_engineer_role_arn" {
  description = "ARN of the data engineer IAM role"
  value       = aws_iam_role.data_engineer_role.arn
}

output "data_scientist_role_arn" {
  description = "ARN of the data scientist IAM role"
  value       = aws_iam_role.data_scientist_role.arn
}

output "data_analyst_role_arn" {
  description = "ARN of the data analyst IAM role"
  value       = aws_iam_role.data_analyst_role.arn
}
