"""
Unit tests for config_utils module.
"""

import json

import pytest
from pydantic import BaseModel, ValidationError

from enterprise_data_engineering.common_utils.config_utils import (
    _deep_update,
    get_env_config,
    load_config,
    merge_configs,
    validate_config,
)


class TestConfig(BaseModel):
    """Test configuration model for testing validation."""

    name: str
    value: int
    enabled: bool = True


@pytest.fixture
def temp_config_files(tmp_path):
    """Create temporary config files for testing."""
    yaml_config = tmp_path / "config.yaml"
    json_config = tmp_path / "config.json"
    invalid_config = tmp_path / "config.txt"

    # Create YAML config
    yaml_content = """
    name: test
    value: 42
    enabled: true
    nested:
      key1: value1
      key2: value2
    """
    yaml_config.write_text(yaml_content)

    # Create JSON config
    json_content = {
        "name": "test-json",
        "value": 100,
        "enabled": False,
        "nested": {"key1": "json-value1", "key2": "json-value2"},
    }
    json_config.write_text(json.dumps(json_content))

    # Create invalid config (not YAML or JSON)
    invalid_config.write_text("This is not a valid config file")

    return {"yaml": yaml_config, "json": json_config, "invalid": invalid_config}


class TestLoadConfig:
    """Tests for the load_config function."""

    def test_load_yaml_config(self, temp_config_files):
        """Test loading a YAML configuration file."""
        config = load_config(temp_config_files["yaml"])

        assert config["name"] == "test"
        assert config["value"] == 42
        assert config["enabled"] is True
        assert config["nested"]["key1"] == "value1"
        assert config["nested"]["key2"] == "value2"

    def test_load_json_config(self, temp_config_files):
        """Test loading a JSON configuration file."""
        config = load_config(temp_config_files["json"])

        assert config["name"] == "test-json"
        assert config["value"] == 100
        assert config["enabled"] is False
        assert config["nested"]["key1"] == "json-value1"
        assert config["nested"]["key2"] == "json-value2"

    def test_load_nonexistent_file(self):
        """Test loading a non-existent file returns empty dict."""
        config = load_config("nonexistent_file.yaml")
        assert config == {}

    def test_load_nonexistent_file_with_default(self):
        """Test loading a non-existent file returns default config."""
        default_config = {"name": "default", "value": 0}
        config = load_config("nonexistent_file.yaml", default_config)
        assert config == default_config

    def test_load_unsupported_format(self, temp_config_files):
        """Test loading an unsupported file format raises ValueError."""
        with pytest.raises(ValueError):
            load_config(temp_config_files["invalid"])

    def test_load_empty_yaml_file(self, tmp_path):
        """Test loading an empty YAML file returns empty dict."""
        empty_file = tmp_path / "empty.yaml"
        empty_file.write_text("")

        config = load_config(empty_file)
        assert config == {}


class TestValidateConfig:
    """Tests for the validate_config function."""

    def test_valid_config(self):
        """Test validating a valid configuration."""
        config = {"name": "test", "value": 42}
        validated = validate_config(config, TestConfig)

        assert isinstance(validated, TestConfig)
        assert validated.name == "test"
        assert validated.value == 42
        assert validated.enabled is True  # Default value

    def test_invalid_config(self):
        """Test validating an invalid configuration raises ValidationError."""
        # Missing required field 'value'
        config = {"name": "test"}

        with pytest.raises(ValidationError):
            validate_config(config, TestConfig)

    def test_additional_fields(self):
        """Test validating a config with additional fields."""
        config = {"name": "test", "value": 42, "extra": "field"}
        validated = validate_config(config, TestConfig)

        assert isinstance(validated, TestConfig)
        assert validated.name == "test"
        assert validated.value == 42
        # Extra field is ignored
        assert not hasattr(validated, "extra")


class TestGetEnvConfig:
    """Tests for the get_env_config function."""

    def test_get_env_config_simple(self, monkeypatch):
        """Test getting config from environment variables."""
        # Set environment variables
        monkeypatch.setenv("TEST_NAME", "env-test")
        monkeypatch.setenv("TEST_VALUE", "100")
        monkeypatch.setenv("TEST_ENABLED", "false")

        config = get_env_config("TEST")

        assert config["name"] == "env-test"
        assert config["value"] == "100"
        assert config["enabled"] == "false"

    def test_get_env_config_nested(self, monkeypatch):
        """Test getting nested config from environment variables."""
        # Set environment variables with nesting
        monkeypatch.setenv("TEST_NESTED__KEY1", "env-value1")
        monkeypatch.setenv("TEST_NESTED__KEY2", "env-value2")

        config = get_env_config("TEST")

        assert config["nested"]["key1"] == "env-value1"
        assert config["nested"]["key2"] == "env-value2"

    def test_get_env_config_custom_delimiter(self, monkeypatch):
        """Test getting nested config with custom delimiter."""
        # Set environment variables with custom delimiter
        monkeypatch.setenv("TEST_NESTED-KEY1", "env-value1")
        monkeypatch.setenv("TEST_NESTED-KEY2", "env-value2")

        config = get_env_config("TEST", nested_delimiter="-")

        assert config["nested"]["key1"] == "env-value1"
        assert config["nested"]["key2"] == "env-value2"

    def test_get_env_config_no_lowercase(self, monkeypatch):
        """Test getting config without lowercasing keys."""
        # Set environment variables
        monkeypatch.setenv("TEST_NAME", "env-test")
        monkeypatch.setenv("TEST_VALUE", "100")

        config = get_env_config("TEST", lowercase_keys=False)

        assert config["NAME"] == "env-test"
        assert config["VALUE"] == "100"

    def test_get_env_config_not_matching_prefix(self, monkeypatch):
        """Test that environment variables not matching prefix are ignored."""
        # Set environment variables
        monkeypatch.setenv("TEST_NAME", "env-test")
        monkeypatch.setenv("OTHER_VALUE", "100")

        config = get_env_config("TEST")

        assert config["name"] == "env-test"
        assert "value" not in config


class TestMergeConfigs:
    """Tests for the merge_configs function."""

    def test_merge_configs_simple(self):
        """Test merging simple configurations."""
        config1 = {"name": "test1", "value": 42}
        config2 = {"name": "test2", "enabled": False}

        merged = merge_configs(config1, config2)

        # Second config should override first
        assert merged["name"] == "test2"
        assert merged["value"] == 42
        assert merged["enabled"] is False

    def test_merge_configs_nested(self):
        """Test merging configurations with nested dictionaries."""
        config1 = {"name": "test1", "nested": {"key1": "value1", "key2": "value2"}}
        config2 = {"name": "test2", "nested": {"key1": "new-value1", "key3": "value3"}}

        merged = merge_configs(config1, config2)

        assert merged["name"] == "test2"
        assert merged["nested"]["key1"] == "new-value1"  # Override
        assert merged["nested"]["key2"] == "value2"  # Preserved
        assert merged["nested"]["key3"] == "value3"  # Added

    def test_merge_multiple_configs(self):
        """Test merging multiple configurations."""
        config1 = {"name": "test1", "value": 42}
        config2 = {"name": "test2", "enabled": False}
        config3 = {"name": "test3", "value": 100}

        merged = merge_configs(config1, config2, config3)

        # Last config should have highest priority
        assert merged["name"] == "test3"
        assert merged["value"] == 100
        assert merged["enabled"] is False

    def test_merge_configs_empty(self):
        """Test merging with empty configurations."""
        config1 = {"name": "test1", "value": 42}
        config2 = {}

        merged = merge_configs(config1, config2)

        assert merged == config1

        # Empty first config
        merged = merge_configs({}, config1)

        assert merged == config1

    def test_deep_update(self):
        """Test the _deep_update helper function."""
        target = {"name": "test", "nested": {"key1": "value1", "key2": "value2"}}
        source = {"name": "updated", "nested": {"key1": "new-value1", "key3": "value3"}}

        # Call the function
        _deep_update(target, source)

        # Check that target was updated in-place
        assert target["name"] == "updated"
        assert target["nested"]["key1"] == "new-value1"
        assert target["nested"]["key2"] == "value2"
        assert target["nested"]["key3"] == "value3"
