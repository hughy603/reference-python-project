#!/bin/bash

# Script to clean up empty directories in the docs/ directory

# Set strict mode
set -euo pipefail

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_DIR="$PROJECT_ROOT/docs"

echo "Starting cleanup of empty directories in docs/..."

# Function to check if a directory is empty or only contains empty directories
is_dir_empty() {
  local dir=$1

  # Check if the directory exists
  if [ ! -d "$dir" ]; then
    return 1  # Not a directory or doesn't exist
  fi

  # Check if directory is empty
  if [ -z "$(ls -A "$dir")" ]; then
    return 0  # Empty directory
  fi

  # Check if it only contains empty directories
  for item in "$dir"/*; do
    if [ -f "$item" ]; then
      return 1  # Contains a file, so not empty
    fi
    if [ -d "$item" ] && ! is_dir_empty "$item"; then
      return 1  # Contains a non-empty directory
    fi
  done

  return 0  # Only contains empty directories
}

# Function to remove empty directory
remove_empty_dir() {
  local dir=$1
  local no_confirm=$2

  if [ ! -d "$dir" ]; then
    echo "Directory does not exist: $dir"
    return
  fi

  if is_dir_empty "$dir"; then
    if [ "$no_confirm" = true ]; then
      rm -rf "$dir"
      echo "Deleted empty directory: $dir"
    else
      read -p "Delete empty directory $dir? [y/N]: " response
      if [[ "$response" =~ ^[Yy]$ ]]; then
        rm -rf "$dir"
        echo "Deleted empty directory: $dir"
      fi
    fi

    # Check if parent directory is now empty
    local parent=$(dirname "$dir")
    if [ "$parent" != "$DOCS_DIR" ] && is_dir_empty "$parent"; then
      if [ "$no_confirm" = true ]; then
        rm -rf "$parent"
        echo "Deleted parent directory (now empty): $parent"
      else
        read -p "Delete parent directory (now empty) $parent? [y/N]: " response
        if [[ "$response" =~ ^[Yy]$ ]]; then
          rm -rf "$parent"
          echo "Deleted parent directory (now empty): $parent"
        fi
      fi
    fi
  else
    echo "Directory is not empty: $dir"
  fi
}

# Parse command line arguments
no_confirm=false
if [ "$#" -gt 0 ] && [ "$1" = "--no-confirm" ]; then
  no_confirm=true
fi

# List of directories to check for removal
dirs_to_check=(
  "examples"
  "infrastructure"
  "user-guide"
  "api"
  "python"
  "windows"
  "architecture/well-architected"
  "development/enterprise"
  "development/python"
  "development/terraform"
  "development/vscode"
  "reference/data_pipelines"
  "reference/examples"
  "reference/spark"
  "reference/common_utils"
  "reference/terraform"
)

# Check and remove specified empty directories
for dir in "${dirs_to_check[@]}"; do
  remove_empty_dir "$DOCS_DIR/$dir" "$no_confirm"
done

# Find and remove any remaining empty directories
find "$DOCS_DIR" -type d -empty -not -path "$DOCS_DIR" | while read -r dir; do
  if [ "$no_confirm" = true ]; then
    rm -rf "$dir"
    echo "Deleted additional empty directory: $dir"
  else
    read -p "Delete additional empty directory $dir? [y/N]: " response
    if [[ "$response" =~ ^[Yy]$ ]]; then
      rm -rf "$dir"
      echo "Deleted additional empty directory: $dir"
    fi
  fi
done

echo "Cleanup of empty directories in docs/ complete!"
