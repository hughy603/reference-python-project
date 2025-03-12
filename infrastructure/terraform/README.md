# Terraform Configuration and Linting

This directory contains Terraform infrastructure configurations along with linting rules and best
practices.

## Linting Setup

We use TFLint for Terraform code linting with strict rules. The configuration is in `.tflint.hcl`.

### Installation

```bash
# Install TFLint
curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash

# Install AWS rules plugin
tflint --init
```

### Usage

```bash
# Run lint from terraform directory
cd infrastructure/terraform
tflint

# Run recursively with detailed output
tflint --recursive --format compact
```

## Best Practices Enforced

- Naming conventions (snake_case for resources, variables)
- Proper documentation for variables and outputs
- Required provider and Terraform version declarations
- Sensitive variable marking
- Unused declarations detection
- AWS-specific best practices
- Security recommendations

## Pre-commit Integration

Our pre-commit hooks automatically run Terraform validation and linting. See the main project
`.pre-commit-config.yaml` file for details.

## CI/CD Validation

The CI/CD pipeline will validate Terraform configurations and fail if linting issues are detected.
Ensure your code passes local linting checks before pushing.

## TFLint Integration

The project now uses TFLint to validate Terraform configurations as part of the pre-commit process.
The following changes were made to ensure proper TFLint functionality:

1. Added `required_version` and `required_providers` blocks to all module files to comply with best
   practices
1. Ensured all AWS resources have the required tags (Environment, Project, Owner)
1. Added proper implementations to modules to address unused variable declarations
1. Applied consistent tag formatting across all resources

To run TFLint manually:

```bash
pre-commit run terraform_tflint
```

Or for more detailed output:

```bash
pre-commit run terraform_tflint --verbose
```
