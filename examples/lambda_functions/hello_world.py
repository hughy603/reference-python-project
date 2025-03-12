"""
Example AWS Lambda function that doesn't require Docker to test locally
"""

import json
import logging
import os
from datetime import datetime

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Sample Lambda function that returns event data and environment information

    Parameters:
    -----------
    event: dict
        The event data passed to the Lambda function
    context: LambdaContext
        The context object with information about the Lambda runtime

    Returns:
    --------
    dict
        Response with event data and environment information
    """
    # Log the received event
    logger.info("Received event: %s", json.dumps(event))

    # Access context properties
    function_name = context.function_name
    remaining_time = context.get_remaining_time_in_millis()

    # Get environment variables
    region = os.environ.get("AWS_REGION", "unknown")
    function_version = os.environ.get("AWS_LAMBDA_FUNCTION_VERSION", "unknown")

    # Process any input from the event
    name = event.get("name", "World")

    # Generate response
    response = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": {
            "message": f"Hello, {name}!",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": {
                "function_name": function_name,
                "function_version": function_version,
                "region": region,
                "remaining_time_ms": remaining_time,
            },
            "event": event,
        },
    }

    return response
