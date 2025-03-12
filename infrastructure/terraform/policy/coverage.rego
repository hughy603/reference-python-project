package terraform

# Default enforcement level
default allow = false

# Require test files for each module
test_exists {
    input.resource_changes[_].type == "module"
    module_name := input.resource_changes[_].name
    test_file := sprintf("test/%s_test.go", [module_name])
    file_exists(test_file)
}

# Verify test coverage threshold is met
coverage_threshold_met {
    coverage := data.coverage_report.percent_covered
    coverage >= 90
}

# Helper function to check if a file exists
file_exists(file) {
    files := input.files
    file_paths := [path | path := files[_].path]
    file_exists_check := [path | path := file_paths[_]; path == file]
    count(file_exists_check) > 0
}

# Check if resource has mandatory tags
has_required_tags(resource) {
    mandatory_tags := {"Environment", "Project", "Owner"}
    resource_tags := {key | resource.change.after.tags[key]}
    missing := mandatory_tags - resource_tags
    count(missing) == 0
}

# Apply tag rules to applicable resources
required_tags_check {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket" # Example: S3 buckets must have tags
    has_required_tags(resource)
}

# Ensure S3 buckets are encrypted
s3_encryption_check {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    resource.change.after.server_side_encryption_configuration
}

# Collect all coverage violations
test_coverage_violations[resource.address] {
    resource := input.resource_changes[_]
    not test_exists
}

# Final decision
allow {
    test_exists
    coverage_threshold_met
    required_tags_check
    s3_encryption_check
    count(test_coverage_violations) == 0
}
