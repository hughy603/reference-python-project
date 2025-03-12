#!/usr/bin/env python3
"""
Run pre-commit hooks with specific configurations.

This script provides shortcuts for running different subsets of pre-commit hooks:
- basic: Run only the most basic hooks that don't require special tools
- lint: Run Python linting hooks
- all: Run all hooks
- ci: Run hooks that would be run in CI
"""

import argparse
import os
import subprocess
import sys


def run_command(command: list[str], env: dict[str, str] | None = None) -> int:
    """Run a command and return its exit code."""
    print(f'Running: {" ".join(command)}')

    # Merge environment variables
    cmd_env = os.environ.copy()
    if env:
        cmd_env.update(env)

    try:
        result = subprocess.run(command, env=cmd_env, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nCommand interrupted by user")
        return 130


def get_hook_groups() -> dict[str, set[str]]:
    """Define groups of hooks."""
    # Basic hooks that are very likely to succeed and don't require special tools
    basic_hooks = {
        "check-yaml",
        "check-json",
        "check-toml",
        "check-added-large-files",
        "trailing-whitespace",
        "end-of-file-fixer",
        "mixed-line-ending",
        "check-merge-conflict",
        "detect-private-key",
        "debug-statements",
    }

    # Python linting hooks
    lint_hooks = basic_hooks | {
        "ruff",
        "ruff-format",
        "bandit",
    }

    # All hooks - empty means don't skip any
    all_hooks = set()

    # Hooks to run in CI - skip hooks that might be problematic
    ci_hooks = set(
        [
            "terraform_validate",
            "terraform_tflint",
            "terraform_docs",
            "terraform_checkov",
            "python-coverage-check",
            "interrogate",
            "gitleaks",
            "check-jsonschema",
            "pip-audit",
        ]
    )

    return {
        "basic": basic_hooks,
        "lint": lint_hooks,
        "all": all_hooks,
        "ci": ci_hooks,
    }


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Run pre-commit hooks with specific configurations"
    )
    parser.add_argument(
        "group", choices=["basic", "lint", "all", "ci"], help="Which group of hooks to run"
    )
    parser.add_argument(
        "--all-files", action="store_true", help="Run on all files, not just staged files"
    )
    parser.add_argument("--files", nargs="+", help="Run on specific files")

    args = parser.parse_args()
    hook_groups = get_hook_groups()

    # For 'all', we don't skip anything
    # For 'ci', we use the inverse logic - skip the hooks in the set
    hooks_to_skip = hook_groups[args.group]

    if args.group == "all":
        env = {}
    elif args.group == "ci":
        env = {"SKIP": ",".join(hooks_to_skip)}
    else:
        # For basic and lint, we specify what to run
        skip_all_except = ",".join(f"^{hook}$" for hook in hooks_to_skip)
        env = {"SKIP_REGEX": f"^(?!({skip_all_except})).*$"}

    cmd = ["pre-commit", "run"]

    if args.all_files:
        cmd.append("--all-files")

    if args.files:
        cmd.extend(["--files"] + args.files)

    return run_command(cmd, env)


if __name__ == "__main__":
    sys.exit(main())
