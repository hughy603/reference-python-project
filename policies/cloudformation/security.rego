package cloudformation.security

import input as cfn_template

# Required tags for all resources
required_tags = ["Owner", "Environment", "CostCenter"]

# Check S3 buckets have encryption enabled
deny[msg] {
    resource := cfn_template.Resources[name]
    resource.Type == "AWS::S3::Bucket"

    not resource.Properties.BucketEncryption

    msg := sprintf("S3 bucket '%s' must have encryption enabled", [name])
}

# Check security groups don't allow unrestricted SSH access
deny[msg] {
    resource := cfn_template.Resources[name]
    resource.Type == "AWS::EC2::SecurityGroup"

    ingress := resource.Properties.SecurityGroupIngress[_]
    ingress.CidrIp == "0.0.0.0/0"
    ingress.FromPort <= 22
    ingress.ToPort >= 22

    msg := sprintf("Security group '%s' allows SSH access from the internet", [name])
}

# Check for required tags on taggable resources
deny[msg] {
    resource := cfn_template.Resources[name]
    taggable_types := ["AWS::S3::Bucket", "AWS::EC2::Instance", "AWS::RDS::DBInstance"]
    resource.Type == taggable_types[_]

    # Either has no tags or missing required tags
    not resource.Properties.Tags

    msg := sprintf("Resource '%s' is missing required tags", [name])
}

deny[msg] {
    resource := cfn_template.Resources[name]
    taggable_types := ["AWS::S3::Bucket", "AWS::EC2::Instance", "AWS::RDS::DBInstance"]
    resource.Type == taggable_types[_]

    tags := resource.Properties.Tags
    keys := [tag.Key | tag := tags[_]]

    missing := required_tags - keys
    count(missing) > 0

    msg := sprintf("Resource '%s' is missing required tags: %v", [name, missing])
}

# Check IAM policies don't grant admin privileges
deny[msg] {
    resource := cfn_template.Resources[name]
    resource.Type == "AWS::IAM::Policy"

    policy_doc := resource.Properties.PolicyDocument
    statement := policy_doc.Statement[_]
    statement.Effect == "Allow"
    statement.Action == "*"
    statement.Resource == "*"

    msg := sprintf("IAM policy '%s' grants wildcard admin privileges", [name])
}

# Check RDS instances are encrypted
deny[msg] {
    resource := cfn_template.Resources[name]
    resource.Type == "AWS::RDS::DBInstance"

    not resource.Properties.StorageEncrypted

    msg := sprintf("RDS instance '%s' must have storage encryption enabled", [name])
}

# Check Lambda functions have a dead letter queue
deny[msg] {
    resource := cfn_template.Resources[name]
    resource.Type == "AWS::Lambda::Function"

    not resource.Properties.DeadLetterConfig

    msg := sprintf("Lambda function '%s' must have a dead letter queue configured", [name])
}
