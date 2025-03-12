#!/usr/bin/env python3
"""
Local AWS Lambda Function Tester

This script helps test AWS Lambda functions locally without Docker.
It simulates Lambda runtime environment features and provides a simple way
to execute and test Lambda functions on Windows without admin rights.

Usage:
    python test_lambda_local.py --file lambda_function.py --handler lambda_handler --event event.json

Requirements:
    - Python 3.6+
    - No administrative privileges needed
"""

import argparse
import importlib.util
import json
import logging
import os
import sys
import time
import traceback
from collections.abc import Callable
from datetime import datetime
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("lambda-local")


class LambdaContext:
    """Simulates the Lambda context object passed to function handlers"""

    def __init__(self, function_name: str, timeout: int = 300):
        self.function_name = function_name
        self.function_version = "$LATEST"
        self.invoked_function_arn = f"arn:aws:lambda:local:000000000000:function:{function_name}"
        self.memory_limit_in_mb = 128
        self.aws_request_id = f"local-{int(time.time() * 1000)}"
        self.log_group_name = f"/aws/lambda/{function_name}"
        self.log_stream_name = (
            f'{datetime.now().strftime("%Y/%m/%d")}/[$LATEST]{self.aws_request_id}'
        )
        self.identity = None
        self.client_context = None

        # Set timeout-related attributes
        self._timeout = timeout
        self._start_time = time.time()

    def get_remaining_time_in_millis(self) -> int:
        """Returns the time remaining in milliseconds before the execution times out"""
        elapsed = int((time.time() - self._start_time) * 1000)
        remaining = max(0, (self._timeout * 1000) - elapsed)
        return remaining

    def log(self, message: str) -> None:
        """Logs a message to CloudWatch Logs (simulated using standard logger)"""
        logger.info(f"LAMBDA LOG: {message}")


class LambdaLocalRunner:
    """Runs Lambda functions locally"""

    def __init__(
        self,
        lambda_file: str,
        handler_name: str,
        event_data: dict[str, Any],
        timeout: int = 300,
        env_vars: dict[str, str] | None = None,
    ):
        self.lambda_file = lambda_file
        self.handler_name = handler_name
        self.event_data = event_data
        self.timeout = timeout
        self.env_vars = env_vars or {}

        # Extract function_name from filename
        self.function_name = os.path.splitext(os.path.basename(lambda_file))[0]

    def load_handler(self) -> Callable:
        """Loads the Lambda function handler from file"""
        try:
            # Resolve the absolute file path
            file_path = os.path.abspath(self.lambda_file)

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Lambda file not found: {file_path}")

            # Extract the module name without .py extension
            module_name = os.path.splitext(os.path.basename(file_path))[0]

            # Load the module dynamically
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load module spec from {file_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Get the handler function
            if "." in self.handler_name:
                # Handle module.function format
                module_part, function_part = self.handler_name.rsplit(".", 1)
                handler_module = getattr(module, module_part)
                handler_function = getattr(handler_module, function_part)
            else:
                # Direct function name
                handler_function = getattr(module, self.handler_name)

            return handler_function
        except Exception as e:
            logger.error(f"Failed to load handler: {e!s}")
            raise

    def setup_environment(self) -> dict[str, str]:
        """Sets up Lambda-like environment variables"""
        # Save original environment to restore later
        original_env = os.environ.copy()

        # Set Lambda-specific environment variables
        lambda_env = {
            "AWS_LAMBDA_FUNCTION_NAME": self.function_name,
            "AWS_LAMBDA_FUNCTION_VERSION": "$LATEST",
            "AWS_LAMBDA_FUNCTION_MEMORY_SIZE": "128",
            "AWS_REGION": "us-east-1",  # Default region
            "AWS_EXECUTION_ENV": "AWS_Lambda_python3.8",
            "LAMBDA_TASK_ROOT": os.path.dirname(os.path.abspath(self.lambda_file)),
            "LAMBDA_RUNTIME_DIR": os.path.dirname(os.path.abspath(self.lambda_file)),
            "TZ": "UTC",
        }

        # Add user-provided environment variables
        lambda_env.update(self.env_vars)

        # Update process environment
        os.environ.update(lambda_env)

        return original_env

    def invoke(self) -> dict[str, Any]:
        """Invokes the Lambda function locally and returns the result"""
        original_env = self.setup_environment()

        try:
            # Create Lambda context
            context = LambdaContext(self.function_name, self.timeout)

            # Load the handler
            handler = self.load_handler()

            # Execute the handler
            logger.info(f"Invoking Lambda function: {self.function_name}")
            logger.info(f"Handler: {self.handler_name}")
            logger.info(f"Event: {json.dumps(self.event_data, indent=2)}")
            logger.info("-" * 60)

            start_time = time.time()
            try:
                response = handler(self.event_data, context)
                duration = (time.time() - start_time) * 1000

                logger.info("-" * 60)
                logger.info(f"Execution completed in {duration:.2f}ms")

                # Format response for better readability
                if isinstance(response, (dict, list)):
                    response_str = json.dumps(response, indent=2)
                else:
                    response_str = str(response)

                logger.info(f"Response: {response_str}")
                return response
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                logger.error("-" * 60)
                logger.error(f"Execution failed after {duration:.2f}ms")
                logger.error(f"Error: {e!s}")
                logger.error(traceback.format_exc())
                raise
        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="AWS Lambda Local Runner")
    parser.add_argument("--file", "-f", required=True, help="Lambda function file path")
    parser.add_argument("--handler", "-h", required=True, help="Lambda handler name")
    parser.add_argument("--event", "-e", help="JSON event file path")
    parser.add_argument(
        "--timeout", "-t", type=int, default=300, help="Function timeout in seconds"
    )
    parser.add_argument("--env-vars", help="JSON file with environment variables")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    return parser.parse_args()


def main():
    args = parse_arguments()

    # Set log level
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Load event data
    if args.event:
        try:
            with open(args.event) as f:
                event_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load event file: {e!s}")
            event_data = {}
    else:
        event_data = {}

    # Load environment variables
    env_vars = {}
    if args.env_vars:
        try:
            with open(args.env_vars) as f:
                env_vars = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load environment variables file: {e!s}")

    # Run the Lambda function
    try:
        runner = LambdaLocalRunner(
            lambda_file=args.file,
            handler_name=args.handler,
            event_data=event_data,
            timeout=args.timeout,
            env_vars=env_vars,
        )
        runner.invoke()
    except Exception as e:
        logger.error(f"Lambda execution failed: {e!s}")
        sys.exit(1)


if __name__ == "__main__":
    main()
