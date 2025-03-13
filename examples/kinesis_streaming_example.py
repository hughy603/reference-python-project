"""
Example AWS Kinesis Streaming Data Pipeline

This is a sample application that demonstrates:
1. Creating a Kinesis client to produce streaming data
2. Using AWS Lambda to process Kinesis streams in real-time
3. Writing processed data to different destinations (S3, DynamoDB)

To run locally:
    python examples/kinesis_streaming_example.py \
        --stream-name test-stream \
        --region us-east-1 \
        --output-bucket test-output-bucket

Requirements:
    - boto3
    - pandas
    - numpy
"""

import argparse
import base64
import datetime
import json
import os
import random
import time
import uuid
from typing import Any

import boto3
import pandas as pd


class KinesisStreamProducer:
    """Example class to generate and send data to a Kinesis stream."""

    def __init__(
        self, stream_name: str, region: str, profile: str = None, local_mode: bool = False
    ):
        """
        Initialize the Kinesis stream producer.

        Args:
            stream_name (str): The name of the Kinesis stream
            region (str): AWS region
            profile (str, optional): AWS profile name to use
            local_mode (bool, optional): Whether to use localstack for local testing
        """
        self.stream_name = stream_name
        self.region = region
        self.local_mode = local_mode

        # Set up Kinesis client
        session_kwargs = {"region_name": region}
        if profile:
            session = boto3.Session(profile_name=profile, **session_kwargs)
        else:
            session = boto3.Session(**session_kwargs)

        kinesis_kwargs = {}
        if local_mode:
            kinesis_kwargs["endpoint_url"] = "http://localhost:4566"

        self.kinesis_client = session.client("kinesis", **kinesis_kwargs)

        # Ensure stream exists (for local testing)
        if local_mode:
            self._ensure_stream_exists()

    def _ensure_stream_exists(self) -> None:
        """Create the Kinesis stream if it doesn't exist (for local testing)."""
        try:
            self.kinesis_client.describe_stream(StreamName=self.stream_name)
            print(f"Stream {self.stream_name} already exists")
        except self.kinesis_client.exceptions.ResourceNotFoundException:
            print(f"Creating stream {self.stream_name}")
            self.kinesis_client.create_stream(StreamName=self.stream_name, ShardCount=1)
            # Wait for stream to become active
            waiter = self.kinesis_client.get_waiter("stream_exists")
            waiter.wait(StreamName=self.stream_name)
            print(f"Stream {self.stream_name} created successfully")

    def generate_records(self, num_records: int = 100) -> list[dict[str, Any]]:
        """
        Generate sample IoT device data records.

        Args:
            num_records (int): Number of records to generate

        Returns:
            List[Dict[str, Any]]: List of generated records
        """
        devices = ["device_" + str(i).zfill(3) for i in range(1, 11)]
        locations = ["east", "west", "north", "south", "central"]

        records = []
        timestamp = datetime.datetime.now()

        for _ in range(num_records):
            device = random.choice(devices)
            record = {
                "device_id": device,
                "timestamp": timestamp.isoformat(),
                "location": random.choice(locations),
                "temperature": round(random.uniform(10, 40), 2),
                "humidity": round(random.uniform(30, 90), 2),
                "pressure": round(random.uniform(980, 1030), 2),
                "battery": round(random.uniform(1, 100), 2),
                "status": random.choice(["active", "idle", "error", "maintenance"]),
            }
            # Add some correlation between values
            if record["status"] == "error":
                record["battery"] = round(max(1, record["battery"] - 30), 2)

            timestamp += datetime.timedelta(seconds=random.randint(1, 60))
            records.append(record)

        return records

    def send_records(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Send records to the Kinesis stream.

        Args:
            records (List[Dict[str, Any]]): Records to send

        Returns:
            Dict[str, Any]: Response from Kinesis PutRecords API
        """
        kinesis_records = []

        for record in records:
            kinesis_records.append(
                {"Data": json.dumps(record), "PartitionKey": record["device_id"]}
            )

        response = self.kinesis_client.put_records(
            Records=kinesis_records, StreamName=self.stream_name
        )

        successful = response["Records"]
        failed = response.get("FailedRecordCount", 0)

        print(f"Sent {len(successful) - failed} records successfully, {failed} failed")
        return response


# Lambda handler function for Kinesis stream processing
def lambda_handler(event, context):
    """
    AWS Lambda handler function to process Kinesis stream records.

    Args:
        event (Dict): Lambda event object containing Kinesis records
        context (LambdaContext): Lambda context object

    Returns:
        Dict[str, Any]: Processing results
    """
    print(f"Received {len(event['Records'])} records from Kinesis")

    # Initialize AWS clients
    s3_client = boto3.client("s3")
    dynamodb = boto3.resource("dynamodb")

    # Get environment variables (would be set in Lambda)
    output_bucket = os.environ.get("OUTPUT_BUCKET", "default-output-bucket")
    metrics_table = os.environ.get("METRICS_TABLE", "device-metrics")
    alerts_table = os.environ.get("ALERTS_TABLE", "device-alerts")

    # Get DynamoDB tables
    metrics_table = dynamodb.Table(metrics_table)
    alerts_table = dynamodb.Table(alerts_table)

    # Process records
    processed_records = []
    alerts = []

    for record in event["Records"]:
        # Decode and parse the Kinesis record
        payload = base64.b64decode(record["kinesis"]["data"])
        data = json.loads(payload)

        # Process the data
        processed_record = process_record(data)
        processed_records.append(processed_record)

        # Check for alerts
        if processed_record["status"] == "error" or processed_record["battery"] < 10:
            alerts.append(
                {
                    "device_id": processed_record["device_id"],
                    "alert_id": str(uuid.uuid4()),
                    "alert_type": "error"
                    if processed_record["status"] == "error"
                    else "low_battery",
                    "timestamp": processed_record["timestamp"],
                    "details": json.dumps(processed_record),
                }
            )

    # Batch write metrics to DynamoDB
    with metrics_table.batch_writer() as batch:
        for record in processed_records:
            batch.put_item(Item=record)

    # Write alerts to DynamoDB
    if alerts:
        with alerts_table.batch_writer() as batch:
            for alert in alerts:
                batch.put_item(Item=alert)

    # Write processed records to S3
    if processed_records:
        # Group records by hour for S3 partitioning
        df = pd.DataFrame(processed_records)
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d-%H")

        # Group by hour and device location
        for (hour, location), group in df.groupby(["hour", "location"]):
            # Convert to CSV
            csv_data = group.to_csv(index=False)

            # Create S3 key with partitioning
            s3_key = f"year={hour[:4]}/month={hour[5:7]}/day={hour[8:10]}/hour={hour[11:13]}/location={location}/{uuid.uuid4()}.csv"

            # Upload to S3
            s3_client.put_object(Bucket=output_bucket, Key=s3_key, Body=csv_data)

    return {
        "statusCode": 200,
        "processed_count": len(processed_records),
        "alerts_count": len(alerts),
    }


def process_record(record):
    """
    Process a single data record with transformations.

    Args:
        record (Dict[str, Any]): Raw data record

    Returns:
        Dict[str, Any]: Processed record
    """
    # Create a copy to avoid mutating the input
    processed = record.copy()

    # Add calculated fields
    processed["processed_at"] = datetime.datetime.now().isoformat()

    # Add a heat index calculation (simplified version)
    if "temperature" in processed and "humidity" in processed:
        t = processed["temperature"]
        h = processed["humidity"]
        # Simple heat index approximation
        heat_index = 0.5 * (t + 61.0 + ((t - 68.0) * 1.2) + (h * 0.094))
        processed["heat_index"] = round(heat_index, 2)

    # Add data quality flags
    processed["data_quality"] = "good"

    # Flag outliers
    if processed.get("temperature", 0) > 35 or processed.get("temperature", 0) < 5:
        processed["data_quality"] = "suspect"

    if processed.get("humidity", 0) > 95 or processed.get("humidity", 0) < 10:
        processed["data_quality"] = "suspect"

    return processed


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Kinesis Stream Producer Example")
    parser.add_argument("--stream-name", required=True, help="Kinesis stream name")
    parser.add_argument("--region", default="us-east-1", help="AWS region")
    parser.add_argument("--profile", help="AWS profile name")
    parser.add_argument("--local", action="store_true", help="Use localstack for local testing")
    parser.add_argument("--records", type=int, default=100, help="Number of records to generate")
    parser.add_argument("--continuous", action="store_true", help="Continuously send data")
    parser.add_argument(
        "--interval", type=int, default=5, help="Interval between batches in seconds"
    )
    parser.add_argument("--output-bucket", help="S3 bucket for processed data (for documentation)")

    args = parser.parse_args()

    # Create producer
    producer = KinesisStreamProducer(
        stream_name=args.stream_name,
        region=args.region,
        profile=args.profile,
        local_mode=args.local,
    )

    if args.continuous:
        print(f"Sending data continuously every {args.interval} seconds. Press Ctrl+C to stop.")
        try:
            batch_num = 1
            while True:
                print(f"Sending batch {batch_num}...")
                records = producer.generate_records(args.records)
                producer.send_records(records)
                batch_num += 1
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("Stopping data production")
    else:
        # Generate and send a single batch
        records = producer.generate_records(args.records)
        producer.send_records(records)
        print(f"Sent {len(records)} records to stream {args.stream_name}")

        # Print example Lambda invocation for local testing
        print("\nExample Lambda event for local testing:")
        example_event = {
            "Records": [
                {
                    "kinesis": {
                        "partitionKey": records[0]["device_id"],
                        "data": json.dumps(records[0]).encode("utf-8").hex(),
                    },
                    "eventSource": "aws:kinesis",
                    "eventID": "shardId-000000000000",
                    "invokeIdentityArn": "arn:aws:iam::123456789012:role/lambda-role",
                    "eventVersion": "1.0",
                    "eventName": "aws:kinesis:record",
                    "eventSourceARN": f"arn:aws:kinesis:{args.region}:123456789012:stream/{args.stream_name}",
                    "awsRegion": args.region,
                }
            ]
        }
        print(json.dumps(example_event, indent=2))
