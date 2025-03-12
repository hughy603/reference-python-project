# Pre-commit Setup and Usage

This project uses [pre-commit](https://pre-commit.com/) to ensure code quality and consistency.
Pre-commit runs hooks on your code before each commit, helping catch issues early.

## Quick Start

```bash
# Install pre-commit (if not already installed)
pip install pre-commit

# Install the pre-commit hooks
pre-commit install

# Run pre-commit on all files
python scripts/run_precommit.py basic --all-files
```

## Helper Scripts

We've created two helper scripts to make working with pre-commit easier:

### 1. `scripts/fix_precommit.py`

This script helps fix common pre-commit issues and performs several helpful tasks:

- Fixes end-of-file newline issues
- Checks if required tools are installed
- Updates pre-commit hooks to the latest versions
- Runs basic pre-commit hooks
- Provides guidance on fixing other issues

Run it with:

```bash
python scripts/fix_precommit.py
```

### 2. `scripts/run_precommit.py`

This script provides easy ways to run different groups of pre-commit hooks:

```bash
# Run only basic hooks (formatting, whitespace, etc.)
python scripts/run_precommit.py basic --all-files

# Run Python linting hooks
python scripts/run_precommit.py lint --all-files

# Run hooks that would be run in CI
python scripts/run_precommit.py ci --all-files

# Run all hooks
python scripts/run_precommit.py all --all-files

# Run on specific files
python scripts/run_precommit.py basic --files path/to/file.py
```

## Available Hooks

Our pre-commit configuration includes the following groups of hooks:

### Basic Hooks

- `check-yaml`: Validates YAML files
- `check-json`: Validates JSON files
- `check-toml`: Validates TOML files
- `check-added-large-files`: Prevents large files from being committed
- `trailing-whitespace`: Removes trailing whitespace
- `end-of-file-fixer`: Ensures files end with a newline
- `mixed-line-ending`: Normalizes line endings
- `check-merge-conflict`: Checks for merge conflict markers
- `detect-private-key`: Prevents committing private keys
- `debug-statements`: Checks for Python debug statements

### Python Linting Hooks

- `ruff`: Fast Python linter (replaces flake8, isort, etc.)
- `ruff-format`: Code formatter (alternative to black)
- `bandit`: Security linter for Python

### Other Specialized Hooks

- `terraform_*`: Various Terraform validation hooks
- `gitleaks`: Detects hardcoded secrets
- `mdformat`: Formats Markdown files
- `pyright`: Type checking
- `interrogate`: Checks docstring coverage

## Troubleshooting

### Common Issues

1. **Missing tools**:

   - Some hooks require external tools (pyright, radon, terraform, etc.)
   - Install the missing tools or skip those hooks

1. **Hook failures**:

   - For linting issues: Fix the reported style issues
   - For YAML/JSON validation: Ensure files are valid or exclude problematic files

### Skipping Hooks

You can temporarily skip specific hooks with:

```bash
SKIP=hook-id git commit -m "Your message"
```

Example:

```bash
SKIP=ruff,ruff-format git commit -m "Work in progress"
```

### Adding Files to Skip Lists

If certain files are causing problems with specific hooks, you can add exclusion patterns in the
`.pre-commit-config.yaml` file:

```yaml
- id: check-yaml
  exclude: ^path/to/problematic/files/.*$
```

## Updating Hooks

To update hooks to their latest versions:

```bash
pre-commit autoupdate
```

## CI Integration

In CI environments, we've configured pre-commit to skip certain hooks that might not work well in
CI. See the `ci.skip` section in `.pre-commit-config.yaml` for details.
