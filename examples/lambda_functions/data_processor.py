"""
Example Lambda function for processing data from S3 and storing metadata in DynamoDB.

This function is triggered by S3 events when new CSV files are uploaded to the 'incoming/' prefix.
It demonstrates a typical ETL workflow where data is:
1. Extracted from S3
2. Transformed (parsed and validated)
3. Loaded (metadata stored in DynamoDB and processed data back to S3)

Usage:
    This module is designed to be deployed as an AWS Lambda function using the
    provided serverless.yml configuration.
"""

import json
import os
import uuid
from datetime import UTC, datetime
from typing import Any

# Note: These imports will be resolved in the Lambda environment when deployed
# Import errors in local development are expected and can be ignored
try:
    import boto3
    import pandas as pd
    from botocore.exceptions import ClientError
except ImportError:
    # For development/testing without required libraries
    pass

# Initialize AWS clients
s3_client = boto3.client("s3") if "boto3" in globals() else None
dynamodb = boto3.resource("dynamodb") if "boto3" in globals() else None
metadata_table = (
    dynamodb.Table(os.environ.get("METADATA_TABLE", "metadata-dev")) if dynamodb else None
)


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Main Lambda handler function.

    Args:
        event: The event dict that contains the parameters sent when the function is invoked.
        context: Lambda context object with runtime information.

    Returns:
        Dict with status and processing results.
    """
    print(f"Processing event: {json.dumps(event)}")

    try:
        # Extract bucket and key from the S3 event
        records = event.get("Records", [])
        if not records:
            return {"statusCode": 400, "body": "No records found in event"}

        results = []
        for record in records:
            s3_event = record.get("s3", {})
            bucket = s3_event.get("bucket", {}).get("name")
            key = s3_event.get("object", {}).get("key")

            if not bucket or not key:
                continue

            # Process the CSV file
            result = process_csv_file(bucket, key)
            results.append(result)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": f"Successfully processed {len(results)} files", "results": results}
            ),
        }

    except Exception as e:
        print(f"Error processing event: {e!s}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "message": f"Error processing event: {e!s}",
                }
            ),
        }


def process_csv_file(bucket: str, key: str) -> dict[str, Any]:
    """
    Process a CSV file from S3.

    Args:
        bucket: S3 bucket name
        key: S3 object key

    Returns:
        Dict with processing results
    """
    try:
        # Download the file from S3
        tmp_file_path = f"/tmp/{uuid.uuid4()}.csv"
        s3_client.download_file(bucket, key, tmp_file_path)

        # Read and validate the CSV data
        df = pd.read_csv(tmp_file_path)

        # Perform data transformations
        df = transform_data(df)

        # Create a processed key for the transformed data
        processed_key = key.replace("incoming/", "processed/")

        # Save the processed data back to S3
        processed_file_path = f"/tmp/{uuid.uuid4()}_processed.csv"
        df.to_csv(processed_file_path, index=False)
        s3_client.upload_file(processed_file_path, bucket, processed_key)

        # Save metadata to DynamoDB using timezone-aware datetime
        now = datetime.now(UTC)
        metadata = {
            "id": str(uuid.uuid4()),
            "timestamp": now.isoformat(),
            "source_bucket": bucket,
            "source_key": key,
            "processed_key": processed_key,
            "row_count": len(df),
            "columns": df.columns.tolist(),
            "processed_at": now.isoformat(),
        }

        metadata_table.put_item(Item=metadata)

        # Clean up temporary files
        os.remove(tmp_file_path)
        os.remove(processed_file_path)

        return {"status": "success", "metadata": metadata}

    except Exception as e:
        print(f"Error processing file {bucket}/{key}: {e!s}")
        # Log the error to DynamoDB for tracking
        now = datetime.now(UTC)
        error_metadata = {
            "id": str(uuid.uuid4()),
            "timestamp": now.isoformat(),
            "source_bucket": bucket,
            "source_key": key,
            "error": str(e),
            "error_type": type(e).__name__,
            "processed_at": now.isoformat(),
        }

        try:
            metadata_table.put_item(Item=error_metadata)
        except ClientError as db_error:
            print(f"Failed to log error to DynamoDB: {db_error!s}")

        return {"status": "error", "error": str(e), "metadata": error_metadata}


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply transformations to the input DataFrame.

    Args:
        df: Input DataFrame

    Returns:
        Transformed DataFrame
    """
    # Example transformations
    # 1. Drop duplicates
    df = df.drop_duplicates()

    # 2. Fill missing values
    df = df.fillna({col: "" if df[col].dtype == "object" else 0 for col in df.columns})

    # 3. Add derived columns
    if "timestamp" in df.columns:
        # Convert timestamp to date without using .dt accessor
        df["date"] = pd.to_datetime(df["timestamp"]).apply(lambda x: x.date())

    # 4. Convert column names to lowercase
    df.columns = [col.lower() for col in df.columns]

    return df


if __name__ == "__main__":
    # For local testing
    test_event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "enterprise-data-dev-bucket"},
                    "object": {"key": "incoming/sample_data.csv"},
                }
            }
        ]
    }
    print(json.dumps(handler(test_event, {}), indent=2))
