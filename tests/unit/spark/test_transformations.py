"""Tests for Spark transformation functions."""

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from enterprise_data_engineering.spark.transformations import (
    add_audit_columns,
    apply_schema_enforcement,
    clean_column_names,
    remove_empty_columns,
    standardize_date_columns,
)


@pytest.fixture(scope="session")
def spark():
    """Create a Spark session for testing."""
    return (
        SparkSession.builder.appName("pytest-spark")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.default.parallelism", "1")
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .getOrCreate()
    )


@pytest.mark.spark
class TestSparkTransformations:
    """Test suite for Spark transformation functions."""

    def test_clean_column_names(self, spark):
        """Test cleaning column names to snake_case."""
        # Arrange
        data = [("value1", "value2")]
        df = spark.createDataFrame(data, ["Column Name", "Another-Column!"])

        # Act
        result = clean_column_names(df)

        # Assert
        assert result.columns == ["column_name", "another_column"]
        assert result.count() == 1

    def test_remove_empty_columns(self, spark):
        """Test removing columns with high null percentages."""
        # Arrange
        data = [(1, None, "value1"), (2, None, "value2"), (3, "rare", "value3")]
        df = spark.createDataFrame(data, ["id", "mostly_null", "non_null"])

        # Act - Remove columns with > 66% nulls
        result = remove_empty_columns(df, threshold=0.66)

        # Assert
        assert "mostly_null" not in result.columns
        assert "id" in result.columns
        assert "non_null" in result.columns

        # Act - With higher threshold that should keep all columns
        result2 = remove_empty_columns(df, threshold=0.8)

        # Assert
        assert "mostly_null" in result2.columns

    def test_add_audit_columns(self, spark):
        """Test adding standard audit columns."""
        # Arrange
        data = [(1, "test")]
        df = spark.createDataFrame(data, ["id", "value"])
        process_name = "test_process"
        source_system = "test_source"

        # Act
        result = add_audit_columns(df, process_name, source_system)

        # Assert
        assert "process_timestamp" in result.columns
        assert "process_name" in result.columns
        assert "source_system" in result.columns
        assert "batch_id" in result.columns

        # Verify values
        first_row = result.collect()[0]
        assert first_row["process_name"] == process_name
        assert first_row["source_system"] == source_system
        assert first_row["batch_id"] is not None

    def test_apply_schema_enforcement(self, spark):
        """Test schema enforcement functionality."""
        # Arrange
        data = [(1, "test")]
        df = spark.createDataFrame(data, ["id", "value"])

        # Target schema with an extra column and different order
        target_schema = StructType(
            [
                StructField("value", StringType(), True),
                StructField("id", IntegerType(), True),
                StructField("extra_column", StringType(), True),
            ]
        )

        # Act - Permissive mode (default)
        result = apply_schema_enforcement(df, target_schema)

        # Assert
        assert result.columns == ["value", "id", "extra_column"]
        assert result.schema["id"].dataType == IntegerType()
        first_row = result.collect()[0]
        assert first_row["extra_column"] is None

        # Act & Assert - Strict mode should raise an error
        with pytest.raises(ValueError):
            apply_schema_enforcement(df, target_schema, mode="strict")

    def test_standardize_date_columns(self, spark):
        """Test standardizing date columns."""
        # Arrange

        # Create DataFrame with various date formats
        data = [
            (1, "2022-01-01", "01/15/2022 08:30:00"),
            (2, "2022-02-15", "02/20/2022 12:15:30"),
        ]
        df = spark.createDataFrame(data, ["id", "simple_date", "complex_date"])

        # Date format mapping
        date_formats = {"complex_date": "MM/dd/yyyy HH:mm:ss"}

        # Act
        result = standardize_date_columns(df, date_formats)

        # Assert
        assert isinstance(result.schema["simple_date"].dataType, TimestampType)
        assert isinstance(result.schema["complex_date"].dataType, TimestampType)

        # Verify values
        rows = result.collect()
        assert rows[0]["simple_date"].year == 2022
        assert rows[0]["simple_date"].month == 1
        assert rows[0]["simple_date"].day == 1

        assert rows[0]["complex_date"].year == 2022
        assert rows[0]["complex_date"].month == 1
        assert rows[0]["complex_date"].day == 15
        assert rows[0]["complex_date"].hour == 8
        assert rows[0]["complex_date"].minute == 30
