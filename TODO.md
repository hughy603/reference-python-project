# TODO List

## Project Limitations

- Developers use Windows locally
- Developers do not have Admin access
- Docker Desktop is not an option
- Keep It Simple Stupid (KISS)

## Active Tasks

### Template Standardization

- [x] Fix non-standard pre-commit configuration
  - [x] Consolidate multiple pre-commit configuration files
  - [x] Update hooks to current versions
  - [x] Fix running `pre-commit run terraform_tflint`
  - [x] Ensure consistent hook configuration across environments
- [x] Standardize project structure
  - [x] Align directory structure with Python best practices
  - [x] Ensure package naming follows conventions
  - [x] Remove template placeholder files and directories
- [x] Normalize configuration files
  - [x] Ensure consistent formatting across all config files
  - [x] Remove deprecated configuration options
  - [x] Add comments explaining configuration choices
- [x] Fix inconsistent documentation formats
  - [x] Standardize docstring style across all modules
  - [x] Ensure README and other markdown files follow consistent format
  - [x] Correct outdated or inaccurate documentation
- [x] Resolve dependency management issues
  - [x] Remove redundant dependency specifications
  - [x] Ensure dependency versions are pinned appropriately
  - [x] Verify compatibility between dependencies
- [x] Simplify project configuration
  - [x] Consolidate pyproject.toml configuration
  - [x] Remove redundant configuration files
  - [x] Simplify test structure
  - [x] Consolidate GitHub Actions workflows
  - [x] Update documentation to reflect consolidated structure

### Infrastructure and Cloud Integration

- [ ] Add utilities for cross-account and cross-region resource management
  - [ ] Implement assume-role patterns
  - [ ] Create multi-region deployment templates
- [ ] Incorporate AWS CDK examples for infrastructure as code
  - [ ] Add CDK constructs for common data infrastructure patterns
  - [ ] Include examples of CDK pipelines
- [ ] Add support for canary deployments
  - [ ] Implement gradual traffic shifting
  - [ ] Create automated rollback mechanisms
- [ ] Develop cost monitoring and optimization utilities
  - [ ] Create cost tracking dashboards
  - [ ] Implement cost anomaly detection

### Security and Compliance

- [ ] Add utilities for dynamic IAM policy generation
  - [ ] Implement least-privilege policy generator
  - [ ] Create IAM policy validation tools
- [ ] Enhance API security components
  - [ ] Standardize security headers
  - [ ] Implement secure response handling patterns
- [ ] Include compliance templates for common regulations
  - [ ] GDPR compliance patterns
  - [ ] HIPAA compliance templates
  - [ ] SOC2 control implementations
- [ ] Enhance audit logging capabilities
  - [ ] Implement immutable audit trails
  - [ ] Create audit log analysis tools
- [ ] Add policy enforcement mechanisms
  - [ ] Implement guardrails for resource deployment
  - [ ] Create data policy enforcement tools

### Data Management

- [ ] Implement data lineage tracking mechanisms
  - [ ] Add metadata capture during pipeline execution
  - [ ] Create visualization tools for data lineage
- [ ] Develop data quality validation framework
  - [ ] Add schema validation components
  - [ ] Implement data quality metrics and checks
- [ ] Create metadata management utilities
  - [ ] Build integration with AWS Glue Data Catalog
  - [ ] Implement searchable metadata repository
- [ ] Add components for real-time stream processing
  - [ ] Implement Kinesis processing patterns
  - [ ] Implement Data Migration Service to ingest Oracle databases
  - [ ] Remove Kafka, prefer native AWS services
- [ ] Support data mesh architectural patterns
  - [ ] Implement domain-oriented ownership
  - [ ] Create data product templates
- [ ] Develop ML pipeline integration
  - [ ] Add connectors to SageMaker pipelines
  - [ ] Implement feature store integration
  - [ ] Create model serving infrastructure

### Testing and Developer Experience

- [ ] Add property-based testing for data transformations
  - [ ] Implement Hypothesis-based test generators
  - [ ] Create test fixtures for common data patterns
- [ ] Develop performance benchmarking utilities
  - [ ] Add baseline performance metrics
  - [ ] Implement regression detection
- [ ] Implement chaos testing for AWS infrastructure
  - [ ] Add controlled failure injection
  - [ ] Create resilience testing framework
- [x] Create interactive project initialization wizard
  - [x] Add script to customize project name, package name, and metadata
  - [x] Replace placeholder values in key files
  - [x] Create minimal package structure automatically
- [x] Add VS Code task shortcuts
  - [x] Create task definitions for common operations
  - [x] Add keyboard shortcuts for frequent development tasks
  - [x] Implement problem matchers for better error reporting
- [x] Implement project health dashboard
  - [x] Create script to show test coverage, linting status, etc.
  - [x] Add visual indicators for project health
  - [x] Display quick action commands
- [ ] Add template update functionality
  - [ ] Create script to pull updates from template repository
  - [ ] Implement selective updates for specific components
  - [ ] Ensure custom code is preserved during updates

### Documentation Improvements

- [ ] Add visual guides and progress indicators
  - [ ] Create a visual flowchart showing the setup process
  - [ ] Add progress indicators (e.g., Step 1 of 5)
  - [ ] Include screenshots of successful installation states
  - [ ] Add a "What You'll Build" section with final result screenshot
- [ ] Create an interactive setup script
  - [ ] Build a single script that automates the entire setup process
  - [ ] Add options for interactive vs. non-interactive setup
  - [ ] Provide visual feedback at each step
  - [ ] Include verification at each major step
- [ ] Add troubleshooting guidance in context
  - [ ] Include common error messages and their solutions
  - [ ] Add troubleshooting callouts after each major step
  - [ ] Create a troubleshooting decision tree
- [ ] Improve multi-platform clarity
  - [ ] Use tabbed sections for platform-specific instructions
  - [ ] Add OS-specific icons for visual distinction
  - [ ] Ensure consistent commands across platforms where possible
- [ ] Add expected output examples
  - [ ] Show example output of successful commands
  - [ ] Highlight key information to look for
  - [ ] Indicate error patterns and what they mean
- [ ] Create quick start video content
  - [ ] Produce a 2-3 minute screencast of the setup process
  - [ ] Add timestamps for different steps
  - [ ] Include captions and narration

### Automation and Job Scheduling

- [x] Enhance CLI capabilities for automation systems
  - [x] Implement structured logging for automated environments
  - [x] Add standardized exit codes for job control systems
  - [x] Create status file generation for job monitoring
  - [x] Add non-interactive mode for all CLI commands
- [x] Add Autosys integration utilities
  - [x] Create JIL definition generation tools
  - [x] Add dependency management capabilities
  - [x] Implement job status reporting
  - [x] Add environment variable handling for Autosys
- [ ] Enhance cross-platform job scheduling
  - [ ] Add Windows Task Scheduler integration
  - [ ] Create Linux crontab management utilities
  - [ ] Implement cloud-based scheduler integration (AWS EventBridge, etc.)
- [ ] Improve error handling for scheduled jobs
  - [ ] Add automatic retry mechanisms
  - [ ] Implement dead-letter patterns for failed jobs
  - [ ] Create notification systems for job failures
- [ ] Add workflow orchestration capabilities
  - [ ] Implement directed acyclic graph (DAG) execution model
  - [ ] Add parallel execution support
  - [ ] Create conditional branching based on job results
  - [ ] Implement timeout and circuit breaker patterns

## Completed Tasks

### Project Structure and Organization

- [x] Remove Sphinx-specific files from docs/sphinx/
- [x] Delete duplicate pre-commit files (`pre-commit-config.yaml` and
  `.pre-commit-config-simple.yaml`)
- [x] Remove the `your_package` directory from src/
- [x] Remove empty workflow files (docs-generate.yml, docs-generate-simple.yml,
  docs-generate-new.yml, infrastructure-validation.yml, ci_backup.yml)
- [x] Use `pyproject.toml` as the single source of truth for dependencies
- [x] Convert redundant `requirements.txt` to reference pyproject.toml
- [x] Standardize module naming convention
- [x] Remove duplicate files and code
  - [x] Identify and eliminate redundant utilities
  - [x] Refactor overlapping functionality
  - [x] Ensure single responsibility for modules
- [x] Standardize coding style
  - [x] Ensure consistent formatting across the codebase
  - [x] Apply naming conventions consistently
  - [x] Add or update docstrings to follow Google style convention
- [x] Simplify project configuration
  - [x] Consolidate pyproject.toml configuration
  - [x] Remove redundant configuration files (setup.py, requirements.txt, tox.ini, etc.)
  - [x] Simplify test structure
  - [x] Consolidate GitHub Actions workflows

### Documentation

- [x] Consolidate documentation systems
  - [x] Choose MkDocs with Material theme as the primary documentation system
  - [x] Remove Sphinx dependencies and configurations
  - [x] Update documentation generation scripts to only use MkDocs
- [x] Simplify documentation structure
  - [x] Organize documentation with a clear hierarchy
  - [x] Eliminate duplicate documentation files
  - [x] Ensure consistent formatting across all docs
- [x] Add contribution guidelines
  - [x] Clarify development setup process
  - [x] Document PR review process
  - [x] Include coding standards and style guide
- [x] Improve architecture documentation
  - [x] Create architecture diagrams with Mermaid
  - [x] Document system components and interactions
  - [x] Add deployment architecture examples
- [x] Enhance example documentation
  - [x] Add more practical code examples with detailed comments
  - [x] Include usage patterns for common AWS data engineering tasks
  - [x] Create step-by-step tutorials for key workflows
- [x] Document alignment with AWS Well-Architected Framework's six pillars
  - [x] Operational excellence
  - [x] Security
  - [x] Reliability
  - [x] Performance efficiency
  - [x] Cost optimization
  - [x] Sustainability

### Infrastructure and Development

- [x] Add container support without Windows Admin or docker desktop in a coorporate environment
  - [x] Create a Dockerfile for development and deployment
  - [x] Add Docker Compose configuration for local development
  - [x] Include container best practices documentation
- [x] Implement user-friendly CLI
  - [x] Add CLI interface using Typer (already in dependencies)
  - [x] Create commands for common tasks (init, test, lint, etc.)
  - [x] Add comprehensive CLI documentation and examples
- [x] Consolidate CI/CD flows into fewer, more comprehensive workflows
- [x] Create a single documentation workflow
- [x] Improve AWS integration examples
  - [x] Include serverless.yml examples for Lambda deployments
- [x] Add CI/CD pipeline templates
  - [x] Create deployment pipeline documentation
  - [x] Document security best practices for CI/CD
- [x] Implement automated secrets rotation mechanisms
  - [x] Integrate with AWS Secrets Manager
  - [x] Add rotation schedule templates
- [x] Enhance local development environment
  - [x] Create development container environments
  - [x] Integrate with LocalStack for AWS service emulation

## Future Consideration (After 1.0.0 Release)

- [x] Enterprise Nexus support

### Project Consolidation

- [x] Create consolidation plan to streamline project structure
- [x] Merge documentation files to reduce redundancy
- [x] Move utility modules from reference_python_project to enterprise_data_engineering
  - [x] Move nexus.py to common_utils as nexus_utils.py
  - [x] Adapt CLI modules to the enterprise_data_engineering structure
- [ ] Remove redundant files after consolidation
- [ ] Update package references in configuration files
- [ ] Complete integration testing to ensure functionality is preserved
- [ ] Update documentation to reflect new structure
- [ ] Simplify pre-commit configuration
