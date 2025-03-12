"""Global pytest fixtures and configuration."""

import os
from collections.abc import Generator
from typing import Any

import pytest

# Set environment variables for Spark tests
os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"  # Required for macOS


def pytest_addoption(parser):
    """Add command-line options for pytest."""
    parser.addoption(
        "--run-spark",
        action="store_true",
        default=False,
        help="Run tests that require a Spark context",
    )
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests",
    )


def pytest_configure(config):
    """Configure custom markers for pytest."""
    config.addinivalue_line("markers", "spark: mark test as requiring Spark context")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")


def pytest_collection_modifyitems(config, items):
    """Skip tests based on command-line options."""
    run_spark = config.getoption("--run-spark")
    run_slow = config.getoption("--run-slow")

    skip_spark = pytest.mark.skip(reason="Need --run-spark option to run Spark tests")
    skip_slow = pytest.mark.skip(reason="Need --run-slow option to run slow tests")

    for item in items:
        if "spark" in item.keywords and not run_spark:
            item.add_marker(skip_spark)
        if "slow" in item.keywords and not run_slow:
            item.add_marker(skip_slow)


@pytest.fixture(scope="session")
def spark_session() -> Generator[Any, None, None]:
    """Create a session-scoped Spark session for tests.

    This is a more robust version of the Spark session fixture that properly handles
    teardown to prevent SparkContext issues between tests.
    """
    try:
        # Only import when this fixture is requested
        from pyspark.sql import SparkSession

        spark = (
            SparkSession.builder.appName("pytest-pyspark-local-testing")
            .master("local[*]")
            .config("spark.sql.shuffle.partitions", "1")
            .config("spark.sql.execution.arrow.pyspark.enabled", "true")
            .config("spark.driver.host", "127.0.0.1")
            .config("spark.driver.bindAddress", "127.0.0.1")
            # Memory configuration for local testing
            .config("spark.driver.memory", "1g")
            .config("spark.executor.memory", "1g")
            .config("spark.ui.showConsoleProgress", "false")
            .config("spark.sql.execution.arrow.enabled", "true")
            # Disable Hive support for simpler testing
            .config("spark.sql.catalogImplementation", "in-memory")
            .getOrCreate()
        )

        # Set log level to reduce noise during tests
        spark.sparkContext.setLogLevel("ERROR")

        yield spark

    finally:
        # Ensure SparkSession is stopped
        try:
            if "spark" in locals():
                spark.stop()
        except Exception:
            pass


@pytest.fixture()
def small_spark_df(spark_session) -> Any:
    """Create a small sample DataFrame for testing."""
    data = [
        (1, "John", "2021-01-15"),
        (2, "Jane", "2021-02-20"),
        (3, "Bob", "2021-03-25"),
        (4, "Alice", "2021-04-30"),
        (5, "Charlie", None),
    ]
    columns = ["id", "name", "date"]
    return spark_session.createDataFrame(data, columns)
