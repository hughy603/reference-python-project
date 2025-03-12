.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: setup
setup: ## Set up development environment (unified setup)
	@echo "Running unified setup script..."
	@python scripts/unified_setup.py

.PHONY: setup-no-admin
setup-no-admin: ## Set up without admin rights
	@echo "Running non-admin setup..."
	@python scripts/unified_setup.py --no-admin

.PHONY: setup-quick
setup-quick: ## Perform a quick setup with minimal dependencies
	@echo "Running quick setup..."
	@python scripts/unified_setup.py --quick

.PHONY: test
test: ## Run tests
	@echo "Running tests..."
	@python -m pytest

.PHONY: coverage
coverage: ## Run tests with coverage
	@echo "Running tests with coverage..."
	@python -m pytest --cov=src --cov-report=term --cov-report=html

.PHONY: lint
lint: ## Run linting checks
	@echo "Running linting checks..."
	@ruff check .

.PHONY: format
format: ## Format code
	@echo "Formatting code..."
	@ruff format .

.PHONY: precommit
precommit: ## Run pre-commit on all files
	@echo "Running pre-commit hooks..."
	@pre-commit run --all-files

.PHONY: docs
docs: ## Build and serve documentation
	@echo "Building and serving documentation..."
	@hatch run docs:serve

.PHONY: docs-build
docs-build: ## Build documentation
	@echo "Building documentation..."
	@hatch run docs:build

.PHONY: build
build: ## Build Python package
	@echo "Building package..."
	@hatch build

.PHONY: clean
clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	@rm -rf dist build .pytest_cache .ruff_cache .coverage .mypy_cache .pytest_cache
	@find . -type d -name __pycache__ -exec rm -rf {} +

.PHONY: check-all
check-all: lint test ## Run all checks (lint, test)
	@echo "All checks passed!"

.PHONY: freeze
freeze: ## Generate requirements.txt from pyproject.toml
	@echo "Generating requirements.txt..."
	@hatch run pip freeze > requirements.txt

.PHONY: venv
venv: ## Create and activate virtual environment
	@echo "Creating virtual environment..."
	@python -m venv .venv
	@echo "Activate with:"
	@echo "  source .venv/bin/activate  # Linux/macOS"
	@echo "  .venv\\Scripts\\activate    # Windows"

.PHONY: diagnostics
diagnostics: ## Run diagnostics for troubleshooting
	@echo "Running diagnostics..."
	@python scripts/diagnostics.py

.PHONY: diagnostics-full
diagnostics-full: ## Run full diagnostics with detailed information
	@echo "Running full diagnostics..."
	@python scripts/diagnostics.py --full

.PHONY: check-deps
check-deps: ## Check for outdated dependencies
	@echo "Checking for outdated dependencies..."
	@pip list --outdated

.PHONY: update-deps
update-deps: ## Update all dependencies to latest versions
	@echo "Updating dependencies..."
	@pip install --upgrade -e ".[dev,docs,test]"

.PHONY: verify-setup
verify-setup: ## Verify the setup is working correctly
	@echo "Verifying setup..."
	@python -c "import sys; import platform; print(f'Python {platform.python_version()} on {platform.system()}')"
	@which python || where python
	@python -m pip --version
	@echo "Checking if package is installed..."
	@python -c "import enterprise_data_engineering; print(f'Package version: {enterprise_data_engineering.__version__}')"
