# Enterprise CloudFormation Standards

This document outlines the enterprise standards for CloudFormation templates to ensure consistent,
secure, and maintainable infrastructure as code.

## Template Structure

### Nested Stack Pattern

All complex CloudFormation deployments should follow this nested stack pattern:

```
root-stack/
├── master.yaml             # Primary stack that references nested stacks
├── parameters/             # Parameter files for each environment
│   ├── dev.json
│   ├── test.json
│   ├── staging.json
│   └── prod.json
└── nested-stacks/          # Nested stack templates by resource category
    ├── network.yaml        # VPC, subnets, routing
    ├── security.yaml       # Security groups, IAM roles, etc.
    ├── compute.yaml        # EC2, Lambda, ECS
    ├── storage.yaml        # S3, EFS, EBS
    └── database.yaml       # RDS, DynamoDB, etc.
```

## Best Practices

1. **Parameters**

   - Use parameter groups and labels for clarity
   - Implement constraints with AllowedValues and AllowedPattern
   - Provide default values for non-critical parameters

1. **Resources**

   - Apply consistent naming conventions using logical IDs
   - Use !Ref and !GetAtt rather than hardcoded values
   - Enforce mandatory tags on all resources

1. **Outputs**

   - Export all values needed by other stacks
   - Follow the naming pattern: `${AWS::StackName}-ResourceName`

1. **Mappings**

   - Use for environment-specific configurations
   - Include mappings for instance types by environment

## Custom Resource Library

Maintain these enterprise custom resources:

1. **ConfigurationValidator** - Validates stack configurations before deployment
1. **ComplianceChecker** - Ensures resources meet compliance requirements
1. **ResourceTagger** - Applies standard tags to resources
1. **SecretRotator** - Automates secret rotation for databases and applications

## Change Management

1. **Validation Workflow**

   - Run cfn-lint validation
   - Execute CloudFormation validate-template
   - Run static security analysis
   - Perform drift detection

1. **Deployment Pattern**

   - Use CloudFormation StackSets for multi-region/account deployments
   - Implement change sets for all production changes
   - Maintain detailed change logs

## Template Guardrails

All templates must include:

1. Encryption for data at rest
1. Standard IAM roles with least privilege
1. VPC endpoint configurations
1. Mandatory resource tagging
1. Standard monitoring and logging
