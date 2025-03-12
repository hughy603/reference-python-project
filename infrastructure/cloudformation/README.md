# CloudFormation Configuration and Linting

This directory contains CloudFormation infrastructure templates along with linting rules and best
practices.

## Linting Setup

We use cfn-lint for CloudFormation templates with strict validation rules. The configuration is in
`.cfnlintrc.yaml`.

### Installation

```bash
# Install cfn-lint
pip install cfn-lint

# Optionally install cfn-nag for additional security checks
gem install cfn-nag
```

### Usage

```bash
# Basic linting
cfn-lint infrastructure/cloudformation/**/*.yaml

# With detailed output
cfn-lint -f pretty infrastructure/cloudformation/**/*.yaml

# Additional security checks with cfn-nag
cfn_nag_scan --input-path infrastructure/cloudformation/
```

## Best Practices Enforced

- Parameter and resource descriptions required
- Strict IAM policy validation
- Security group rule validation
- Required encryption for sensitive services
- Required tags (Environment, Project, Owner, CostCenter)
- DynamoDB table provisioning and encryption
- S3 bucket policy requirements
- Resource property validation

## Pre-commit Integration

Our pre-commit hooks automatically run CloudFormation validation and linting. See the main project
`.pre-commit-config.yaml` file for details.

## CI/CD Validation

The CI/CD pipeline will validate CloudFormation templates and fail if linting issues are detected.
Ensure your templates pass local linting checks before pushing.

## Template Structure

Templates should follow this organization:

```
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Required detailed description of the template'

Metadata:
  # Any metadata including AWS::CloudFormation::Interface

Parameters:
  # All parameters with descriptions and constraints

Mappings:
  # Any mappings

Conditions:
  # Any conditions

Resources:
  # Resources with descriptions and required tags

Outputs:
  # Outputs with descriptions
```
