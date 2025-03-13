#!/usr/bin/env python
"""
Python 3.12 Optimization Script

This script demonstrates how to use Python 3.12 optimization features
and provides a convenient way to run your code with optimizations.

Usage:
    python scripts/optimize_py312.py your_script.py [args...]

Environment variables:
    PY_OPTIMIZATION: Set optimization level (0, 1, or 2)
        0 = No optimization
        1 = Skip assert statements
        2 = Skip assert statements and docstrings
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run Python script with Python 3.12 optimizations")
    parser.add_argument("script", help="Path to the Python script to run")
    parser.add_argument("script_args", nargs="*", help="Arguments to pass to the script")
    parser.add_argument(
        "--optimization-level",
        "-O",
        type=int,
        choices=[0, 1, 2],
        default=int(os.environ.get("PY_OPTIMIZATION", "0")),
        help="Optimization level (0=none, 1=skip asserts, 2=skip asserts+docstrings)",
    )
    parser.add_argument(
        "--benchmark",
        "-b",
        action="store_true",
        help="Run the script multiple times and report timing statistics",
    )
    parser.add_argument(
        "--iterations",
        "-i",
        type=int,
        default=5,
        help="Number of iterations for benchmarking (default: 5)",
    )

    return parser.parse_args()


def run_script(script_path, script_args, optimization_level):
    """Run a Python script with the specified optimization level."""
    env = os.environ.copy()

    if optimization_level > 0:
        env["PYTHONOPTIMIZE"] = str(optimization_level)

    cmd = [sys.executable]

    # Add optimization flags through command line as well
    if optimization_level >= 1:
        cmd.append("-O")  # Skip assert statements
    if optimization_level >= 2:
        cmd.append("-O")  # Second -O skips docstrings too

    cmd.append(script_path)
    cmd.extend(script_args)

    print(f"Running: {' '.join(cmd)}")
    print(f"Optimization level: {optimization_level}")

    start_time = time.time()
    result = subprocess.run(cmd, env=env, check=False)
    elapsed = time.time() - start_time

    return result.returncode, elapsed


def benchmark_script(script_path, script_args, optimization_level, iterations=5):
    """Benchmark a script by running it multiple times."""
    print(f"Benchmarking with {iterations} iterations...")

    times = []
    for i in range(iterations):
        print(f"Run {i + 1}/{iterations}:", end=" ", flush=True)
        _, elapsed = run_script(script_path, script_args, optimization_level)
        times.append(elapsed)
        print(f"{elapsed:.4f} seconds")

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print("\nBenchmark Results:")
    print(f"  Average time: {avg_time:.4f} seconds")
    print(f"  Minimum time: {min_time:.4f} seconds")
    print(f"  Maximum time: {max_time:.4f} seconds")
    print(f"  Total time:   {sum(times):.4f} seconds")

    return avg_time


def main():
    """Main function."""
    # Verify Python version
    if sys.version_info < (3, 12):
        print("Warning: This script is designed for Python 3.12 or newer.")
        print(f"Current Python version: {sys.version}")

    args = parse_args()
    script_path = args.script

    if not Path(script_path).exists():
        print(f"Error: Script '{script_path}' not found.")
        return 1

    if args.benchmark:
        benchmark_script(script_path, args.script_args, args.optimization_level, args.iterations)
    else:
        return_code, elapsed = run_script(script_path, args.script_args, args.optimization_level)
        print(f"Script completed in {elapsed:.4f} seconds with return code {return_code}")
        return return_code

    return 0


if __name__ == "__main__":
    sys.exit(main())
