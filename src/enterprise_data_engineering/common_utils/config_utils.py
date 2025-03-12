"""
Configuration utilities for data engineering applications.

This module provides functions for loading, validating, and managing
configuration from YAML, JSON, and environment variables.
"""

import json
import os
import pathlib
from typing import Any

import yaml
from pydantic import BaseModel


def load_config(
    file_path: str | pathlib.Path, default_config: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Load configuration from a YAML or JSON file.

    Args:
        file_path: Path to the configuration file
        default_config: Default configuration to use if file doesn't exist

    Returns:
        Dictionary with configuration values

    Raises:
        ValueError: If the file format is not supported

    Examples:
        >>> config = load_config("config.yaml")
        >>> "database" in config
        True
    """
    path = pathlib.Path(file_path)

    if not path.exists():
        if default_config is not None:
            return default_config
        return {}

    extension = path.suffix.lower()

    with open(path) as f:
        if extension in (".yaml", ".yml"):
            return yaml.safe_load(f) or {}
        elif extension == ".json":
            return json.load(f)
        else:
            raise ValueError(f"Unsupported config file format: {extension}")


def validate_config(config: dict[str, Any], model: type[BaseModel]) -> BaseModel:
    """Validate configuration using a Pydantic model.

    Args:
        config: Configuration dictionary to validate
        model: Pydantic model class to validate against

    Returns:
        Validated configuration as a Pydantic model instance

    Raises:
        ValidationError: If configuration is invalid

    Examples:
        >>> from pydantic import BaseModel
        >>> class DatabaseConfig(BaseModel):
        ...     host: str
        ...     port: int
        >>> config = validate_config({"host": "localhost", "port": 5432}, DatabaseConfig)
        >>> config.host
        'localhost'
    """
    return model.model_validate(config)


def get_env_config(
    prefix: str, lowercase_keys: bool = True, nested_delimiter: str = "__"
) -> dict[str, Any]:
    """Load configuration from environment variables with a common prefix.

    Args:
        prefix: Prefix for environment variables to include
        lowercase_keys: Whether to convert keys to lowercase
        nested_delimiter: Delimiter for creating nested dictionaries

    Returns:
        Dictionary with configuration from environment variables

    Examples:
        >>> # With environment variables APP_DB_HOST=localhost and APP_DB_PORT=5432
        >>> config = get_env_config("APP_")
        >>> config["db"]["host"]
        'localhost'
    """
    result: dict[str, Any] = {}

    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue

        # Remove prefix and standardize key case if needed
        config_key = key[len(prefix) :]
        if lowercase_keys:
            config_key = config_key.lower()

        # Handle nested configuration with delimiter
        if nested_delimiter in config_key:
            parts = config_key.split(nested_delimiter)
            current = result

            # Navigate to the correct level of nesting
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Set the actual value
            current[parts[-1]] = value
        else:
            result[config_key] = value

    return result


def merge_configs(*configs: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple configuration dictionaries.

    Later configurations override values from earlier ones.

    Args:
        *configs: Configuration dictionaries to merge

    Returns:
        Merged configuration dictionary

    Examples:
        >>> default_config = {"debug": False, "port": 8080}
        >>> user_config = {"debug": True}
        >>> merged = merge_configs(default_config, user_config)
        >>> merged["debug"]
        True
        >>> merged["port"]
        8080
    """
    result: dict[str, Any] = {}

    for config in configs:
        _deep_update(result, config)

    return result


def _deep_update(target: dict[str, Any], source: dict[str, Any]) -> None:
    """Recursively update a target dictionary with values from a source dictionary.

    Args:
        target: Target dictionary to update
        source: Source dictionary with new values
    """
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_update(target[key], value)
        else:
            target[key] = value
