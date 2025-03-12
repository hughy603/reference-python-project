# Enterprise Terraform Module Structure

This directory contains reusable Terraform modules that follow enterprise best practices.

## Module Structure

All modules should follow this standardized structure:

```
module-name/
├── README.md           # Documentation with examples and input/output details
├── main.tf             # Primary module logic
├── variables.tf        # Input variable definitions
├── outputs.tf          # Output definitions
├── versions.tf         # Required providers and versions
├── data.tf             # Data sources
├── locals.tf           # Local values
├── examples/           # Example implementations
│   └── basic/          # Basic implementation example
├── test/               # Automated tests
└── modules/            # Nested modules (if needed)
```

## Module Development Guidelines

1. **Versioning**: Tag all modules with semantic versions
1. **Documentation**: Use terraform-docs to generate consistent documentation
1. **Testing**: Implement automated tests using Terratest or equivalent
1. **Compliance**: All modules must pass security and compliance checks

## Example Usage Pattern

```hcl
module "example" {
  source  = "git::https://example.com/repo.git//modules/example?ref=v1.0.0"

  # Required parameters
  region     = "us-west-2"
  account_id = "123456789012"

  # Optional parameters with defaults
  enable_logging = true

  # Example of feature flags
  features = {
    encryption   = true
    replication = false
  }
}
```

## Module Registry

Internal modules should be published to the organization's private module registry for consistent
reuse across teams.
