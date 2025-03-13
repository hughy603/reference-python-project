#!/usr/bin/env python
"""
Comprehensive cleanup and consolidation runner.

This script runs both the cleanup and documentation consolidation scripts
to streamline the project structure and documentation.
"""

import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


def run_script(script_path, *args):
    """Run a Python script with given arguments."""
    try:
        cmd = ["python3", str(script_path)] + list(args)
        logger.info(f"Running: {' '.join(cmd)}")

        result = subprocess.run(
            cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        logger.info(f"Output: {result.stdout}")

        if result.stderr:
            logger.warning(f"Stderr: {result.stderr}")

        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running {script_path}: {e}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        return False


def main():
    """Run the cleanup and consolidation process."""
    logger.info("Starting comprehensive cleanup and consolidation...")

    # 1. Run the cleanup script
    cleanup_script = SCRIPTS_DIR / "cleanup_project.py"
    if not cleanup_script.exists():
        logger.error(f"Cleanup script not found at {cleanup_script}")
        return

    success = run_script(cleanup_script, "--no-confirm")
    if not success:
        logger.error("Cleanup script failed, stopping process")
        return

    # 2. Run the consolidation script
    consolidation_script = SCRIPTS_DIR / "consolidate_docs.py"
    if not consolidation_script.exists():
        logger.error(f"Consolidation script not found at {consolidation_script}")
        return

    success = run_script(consolidation_script)
    if not success:
        logger.error("Consolidation script failed")
        return

    logger.info("Cleanup and consolidation completed successfully!")
    logger.info("Project structure has been streamlined and documentation has been updated.")
    logger.info("Please review the changes and commit them if satisfactory.")


if __name__ == "__main__":
    main()
