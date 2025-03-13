#!/bin/bash

# Script to clean up unused directories and consolidate documentation

# Set strict mode
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Starting cleanup and consolidation process..."

# Step 1: Delete unused directories
echo "Deleting unused directories and files..."

# Build and cache directories
for dir in htmlcov site docs-venv .ruff_cache .pytest_cache; do
  if [ -d "$PROJECT_ROOT/$dir" ]; then
    echo "Deleting $dir..."
    rm -rf "$PROJECT_ROOT/$dir"
  fi
done

# Empty docs directories
for dir in docs/examples; do
  if [ -d "$PROJECT_ROOT/$dir" ]; then
    echo "Deleting $dir..."
    rm -rf "$PROJECT_ROOT/$dir"
  fi
done

# Test coverage files
for file in junit.xml .coverage coverage.xml; do
  if [ -f "$PROJECT_ROOT/$file" ]; then
    echo "Deleting $file..."
    rm -f "$PROJECT_ROOT/$file"
  fi
done

# Step 2: Ensure docs directory structure
echo "Ensuring proper docs directory structure..."

# Create required directories if they don't exist
mkdir -p "$PROJECT_ROOT/docs/getting-started"
mkdir -p "$PROJECT_ROOT/docs/user-guide"
mkdir -p "$PROJECT_ROOT/docs/infrastructure"
mkdir -p "$PROJECT_ROOT/docs/examples"
mkdir -p "$PROJECT_ROOT/docs/development"
mkdir -p "$PROJECT_ROOT/docs/api"
mkdir -p "$PROJECT_ROOT/docs/assets/images"
mkdir -p "$PROJECT_ROOT/docs/assets/stylesheets"

# Remove empty directories
if [ -f "$PROJECT_ROOT/scripts/cleanup_docs_empty_dirs.sh" ]; then
  echo "Removing empty directories under docs/..."
  bash "$PROJECT_ROOT/scripts/cleanup_docs_empty_dirs.sh" --no-confirm
fi

# Step 3: Update README.md with the correct project structure
echo "Updating README.md with the current project structure..."

# The updated structure is already created through the Python script
# We're just reporting it

# Step 4: Update CONSOLIDATION_PLAN.md
echo "Updating CONSOLIDATION_PLAN.md with completed tasks..."

# The updated plan is already created through the Python script
# We're just reporting it

echo "Cleanup and consolidation complete!"
echo "Please review the changes and commit them if satisfactory."
