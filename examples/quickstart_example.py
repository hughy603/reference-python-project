#!/usr/bin/env python
"""
Quickstart Example for Enterprise Data Engineering

This example demonstrates the basic usage pattern for the enterprise_data_engineering
package including configuration loading, logging setup, and data processing.

Usage:
    python quickstart_example.py
"""

import logging
from pathlib import Path

import pandas as pd
import yaml
from rich.console import Console
from rich.logging import RichHandler

# Set up rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger("quickstart")

# Define paths
CURRENT_DIR = Path(__file__).parent
CONFIG_PATH = CURRENT_DIR / "config_example.yaml"


def load_config(config_path: Path) -> dict:
    """Load and return configuration from YAML file."""
    if not config_path.exists():
        log.warning(f"Config file {config_path} not found. Creating example config.")
        example_config = {
            "data": {"input_path": "data/input", "output_path": "data/output", "format": "parquet"},
            "processing": {"batch_size": 1000, "columns_to_keep": ["id", "name", "value"]},
        }

        # Write example config
        with open(config_path, "w") as f:
            yaml.dump(example_config, f, default_flow_style=False)

        return example_config

    log.info(f"Loading config from {config_path}")
    with open(config_path) as f:
        return yaml.safe_load(f)


def create_example_data() -> pd.DataFrame:
    """Create example data for demonstration."""
    log.info("Creating example dataset")
    return pd.DataFrame(
        {
            "id": range(1, 101),
            "name": [f"Item {i}" for i in range(1, 101)],
            "value": [i * 10 for i in range(1, 101)],
            "extra_col": ["extra" for _ in range(100)],
        }
    )


def process_data(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Process data according to configuration."""
    log.info("Processing data")

    # Filter columns based on config
    columns_to_keep = config["processing"]["columns_to_keep"]
    log.info(f"Keeping columns: {columns_to_keep}")

    # Return processed dataframe
    return df[columns_to_keep]


def save_data(df: pd.DataFrame, config: dict) -> None:
    """Save processed data to the specified output path."""
    output_format = config["data"]["format"]
    output_dir = Path(config["data"]["output_path"])

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"processed_data.{output_format}"
    log.info(f"Saving data to {output_path}")

    # Save based on format
    if output_format == "csv":
        df.to_csv(output_path, index=False)
    elif output_format == "parquet":
        df.to_parquet(output_path, index=False)
    else:
        log.error(f"Unsupported format: {output_format}")
        raise ValueError(f"Unsupported format: {output_format}")


def main():
    """Main entry point."""
    console = Console()
    console.rule("[bold blue]Enterprise Data Engineering Quickstart Example")

    # Load configuration
    config = load_config(CONFIG_PATH)

    # Create example data
    df = create_example_data()
    console.print("Original data sample (first 5 rows):", style="bold green")
    console.print(df.head())

    # Process data
    processed_df = process_data(df, config)
    console.print("\nProcessed data sample (first 5 rows):", style="bold green")
    console.print(processed_df.head())

    # Save data
    save_data(processed_df, config)

    console.rule("[bold blue]Processing Complete")
    log.info("Quickstart example completed successfully")


if __name__ == "__main__":
    main()
