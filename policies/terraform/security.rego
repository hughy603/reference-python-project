package terraform.security

import input as tfplan

# Deny S3 buckets without encryption
deny[msg] {
    resource := tfplan.resource_changes[_]
    resource.type == "aws_s3_bucket"
    resource.change.after.server_side_encryption_configuration == null

    msg := sprintf("S3 bucket '%s' must have encryption enabled", [resource.name])
}

# Deny unrestricted security group ingress
deny[msg] {
    resource := tfplan.resource_changes[_]
    resource.type == "aws_security_group_rule"
    resource.change.after.type == "ingress"
    resource.change.after.cidr_blocks[_] == "0.0.0.0/0"
    resource.change.after.from_port <= 22
    resource.change.after.to_port >= 22

    msg := sprintf("Security group rule '%s' allows SSH access from the internet", [resource.name])
}

# Ensure all resources are tagged with required tags
required_tags = ["Owner", "Environment", "CostCenter"]

deny[msg] {
    resource := tfplan.resource_changes[_]
    tags := resource.change.after.tags
    tags != null

    missing := required_tags - object.keys(tags)
    count(missing) > 0

    msg := sprintf("Resource '%s' is missing required tags: %v", [resource.address, missing])
}

# Ensure IAM policies do not grant admin privileges
deny[msg] {
    resource := tfplan.resource_changes[_]
    resource.type == "aws_iam_policy"

    policy := json.unmarshal(resource.change.after.policy)
    statement := policy.Statement[_]
    statement.Effect == "Allow"
    statement.Action == "*"
    statement.Resource == "*"

    msg := sprintf("IAM policy '%s' grants wildcard admin privileges", [resource.name])
}

# Ensure RDS instances are encrypted
deny[msg] {
    resource := tfplan.resource_changes[_]
    resource.type == "aws_db_instance"
    not resource.change.after.storage_encrypted

    msg := sprintf("RDS instance '%s' must have storage encryption enabled", [resource.name])
}

# Ensure Lambda functions are configured with a dead letter queue
deny[msg] {
    resource := tfplan.resource_changes[_]
    resource.type == "aws_lambda_function"
    not resource.change.after.dead_letter_config

    msg := sprintf("Lambda function '%s' must have a dead letter queue configured", [resource.name])
}
