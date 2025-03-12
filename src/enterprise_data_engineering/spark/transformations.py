"""Common Spark data transformation functions for enterprise use cases."""

import pyspark.sql.functions as F
from pyspark.sql import DataFrame
from pyspark.sql.types import StructType


def clean_column_names(df: DataFrame) -> DataFrame:
    """Standardize column names by converting to snake_case.

    This function:
    - Converts all column names to lowercase
    - Replaces spaces and special characters with underscores
    - Removes consecutive underscores

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with cleaned column names
    """
    import re

    # Function to convert a name to snake_case
    def to_snake_case(name: str) -> str:
        # Convert to lowercase
        s = name.lower()
        # Replace non-alphanumeric characters with underscores
        s = re.sub(r"[^a-z0-9]", "_", s)
        # Replace consecutive underscores with a single underscore
        s = re.sub(r"_+", "_", s)
        # Remove leading/trailing underscores
        s = s.strip("_")
        return s

    # Get current column names and create mapping to new names
    old_cols = df.columns
    new_cols = [to_snake_case(col) for col in old_cols]

    # Apply column name changes
    return df.toDF(*new_cols)


def remove_empty_columns(df: DataFrame, threshold: float = 0.9) -> DataFrame:
    """Remove columns that have a high percentage of nulls.

    Args:
        df: Input DataFrame
        threshold: Minimum fraction of NULL values to consider a column for removal
                  (default is 0.9, meaning 90% or more NULL values)

    Returns:
        DataFrame with high-null columns removed
    """
    # Get the total row count
    row_count = df.count()

    if row_count == 0:
        return df  # Return the original DataFrame if it's empty

    # Calculate NULL count for each column
    null_counts = {}
    for column in df.columns:
        null_count = df.filter(F.col(column).isNull()).count()
        null_counts[column] = null_count / row_count

    # Filter out columns with high NULL percentage
    columns_to_keep = [column for column in df.columns if null_counts.get(column, 0) < threshold]

    # Select only the columns to keep
    return df.select(*columns_to_keep)


def add_audit_columns(
    df: DataFrame, process_name: str, source_system: str | None = None
) -> DataFrame:
    """Add standard audit columns to a DataFrame.

    Adds:
    - process_timestamp: When data was processed
    - process_name: Name of the ETL/ELT process
    - source_system: Original data source identifier
    - batch_id: Unique batch identifier

    Args:
        df: Input DataFrame
        process_name: Name of the current process
        source_system: Name of the source system (optional)

    Returns:
        DataFrame with audit columns added
    """
    import uuid

    # Add audit columns
    result = df.withColumn("process_timestamp", F.current_timestamp())
    result = result.withColumn("process_name", F.lit(process_name))

    # Add source system if provided
    if source_system:
        result = result.withColumn("source_system", F.lit(source_system))

    # Add batch ID using UUID
    batch_id = str(uuid.uuid4())
    result = result.withColumn("batch_id", F.lit(batch_id))

    return result


def apply_schema_enforcement(
    df: DataFrame, schema: StructType, mode: str = "permissive"
) -> DataFrame:
    """Enforce a schema on a DataFrame, handling extra/missing columns.

    Args:
        df: Input DataFrame
        schema: Target schema to enforce
        mode: How to handle schema mismatches:
              - 'permissive': Handle extra/missing columns gracefully
              - 'strict': Fail on any schema mismatch

    Returns:
        DataFrame with enforced schema

    Raises:
        ValueError: If mode='strict' and schema doesn't match
    """
    # Get current and target column sets
    current_cols = set(df.columns)
    target_cols = {field.name for field in schema.fields}

    # Check for extra columns
    extra_cols = current_cols - target_cols

    # Check for missing columns
    missing_cols = target_cols - current_cols

    if mode == "strict" and (extra_cols or missing_cols):
        raise ValueError(
            f"Schema mismatch! Extra columns: {extra_cols}, Missing columns: {missing_cols}"
        )

    # Start with original DataFrame
    result = df

    # Drop extra columns if they exist
    if extra_cols:
        result = result.drop(*extra_cols)

    # Add missing columns with NULL values
    for col_name in missing_cols:
        field = next(field for field in schema.fields if field.name == col_name)
        result = result.withColumn(col_name, F.lit(None).cast(field.dataType))

    # Reorder columns to match schema
    ordered_cols = [field.name for field in schema.fields]
    result = result.select(*ordered_cols)

    # Apply the schema (for data type enforcement)
    return result.select(
        *[F.col(c).cast(t.dataType) for c, t in zip(result.columns, schema.fields, strict=False)]
    )


def standardize_date_columns(
    df: DataFrame, date_formats: dict[str, str] = None, date_columns: list[str] = None
) -> DataFrame:
    """Standardize date/timestamp columns to consistent formats.

    Args:
        df: Input DataFrame
        date_formats: Dict mapping column names to their current format
                     (if None, attempts automatic parsing)
        date_columns: List of columns to convert to dates
                     (if None, attempts to infer date columns)

    Returns:
        DataFrame with standardized date columns
    """
    if date_formats is None:
        date_formats = {}

    # If no date columns are specified, look for columns with "date" or "time" in the name
    if date_columns is None:
        date_columns = [
            col
            for col in df.columns
            if any(keyword in col.lower() for keyword in ["date", "time", "dt", "_at", "_on"])
        ]

    result = df

    # Process each date column
    for col_name in date_columns:
        if col_name not in df.columns:
            continue

        # If format is provided, use it; otherwise try to parse automatically
        if col_name in date_formats:
            result = result.withColumn(
                col_name, F.to_timestamp(F.col(col_name), date_formats[col_name])
            )
        else:
            # Try automatic conversion
            result = result.withColumn(col_name, F.to_timestamp(F.col(col_name)))

    return result
