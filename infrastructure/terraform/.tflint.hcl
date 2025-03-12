config {
  format     = "compact"
  plugin_dir = "~/.tflint.d/plugins"

  # Use call_module_type instead of module (required for tflint >= v0.54.0)
  call_module_type = "all"
}

# AWS plugin configuration
plugin "aws" {
  enabled = true
  version = "0.29.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

# Essential rules for better developer experience
# Focus on critical validations that could cause production issues

# Syntax and deprecation checks
rule "terraform_deprecated_interpolation" { enabled = true }
rule "terraform_deprecated_index" { enabled = true }
rule "terraform_unused_declarations" { enabled = true }

# Documentation quality
rule "terraform_documented_outputs" { enabled = true }
rule "terraform_documented_variables" { enabled = true }

# Configuration quality
rule "terraform_required_version" { enabled = true }
rule "terraform_required_providers" { enabled = true }
rule "terraform_unused_required_providers" { enabled = true }

# AWS specific rules
rule "aws_resource_missing_tags" {
  enabled = true
  tags    = ["Environment", "Project", "Owner"]
}
