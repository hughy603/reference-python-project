"""
Data processing pipeline framework.

This module provides a framework for creating data processing pipelines
with clear stages, monitoring, and error handling.
"""

import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Generic, TypeVar, cast

# Define type variables for pipeline input and output
I = TypeVar("I")  # Input type
O = TypeVar("O")  # Output type
T = TypeVar("T")  # Intermediate type


class PipelineStatus(Enum):
    """Status of pipeline execution."""

    NOT_STARTED = auto()
    RUNNING = auto()
    SUCCEEDED = auto()
    FAILED = auto()
    SKIPPED = auto()


@dataclass
class PipelineContext:
    """Shared context for pipeline execution.

    This class stores shared state and metadata that can be accessed
    by all pipeline stages during execution.

    Attributes:
        execution_id: Unique identifier for this pipeline run
        start_time: Timestamp when the pipeline started
        end_time: Timestamp when the pipeline completed, if finished
        parameters: Runtime parameters for the pipeline
        metrics: Metrics collected during pipeline execution
        artifacts: Output artifacts produced during pipeline execution
        status: Current pipeline execution status
    """

    execution_id: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, Any] = field(default_factory=dict)
    status: PipelineStatus = PipelineStatus.NOT_STARTED

    def add_metric(self, name: str, value: Any) -> None:
        """Add a named metric to the pipeline context.

        Args:
            name: Name of the metric
            value: Value of the metric
        """
        self.metrics[name] = value

    def add_artifact(self, name: str, artifact: Any) -> None:
        """Add a named artifact to the pipeline context.

        Args:
            name: Name of the artifact
            artifact: The artifact object
        """
        self.artifacts[name] = artifact


class PipelineStage(Generic[I, O], ABC):
    """Abstract base class for a pipeline processing stage.

    Attributes:
        name: Name of the pipeline stage
        logger: Logger instance for this stage
    """

    def __init__(self, name: str):
        """Initialize a pipeline stage.

        Args:
            name: Name of the pipeline stage
        """
        self.name = name
        self.logger = logging.getLogger(f"pipeline.stage.{name}")

    @abstractmethod
    def process(self, input_data: I, context: PipelineContext) -> O:
        """Process the input data and return the output.

        Args:
            input_data: Input data to process
            context: Shared pipeline context

        Returns:
            Processed output data

        Raises:
            Exception: If processing fails
        """
        pass


class Pipeline(Generic[I, O]):
    """A data processing pipeline composed of multiple stages.

    Attributes:
        name: Name of the pipeline
        stages: List of processing stages
        logger: Logger instance for this pipeline
    """

    def __init__(self, name: str):
        """Initialize a pipeline.

        Args:
            name: Name of the pipeline
        """
        self.name = name
        self.stages: list[PipelineStage[Any, Any]] = []
        self.logger = logging.getLogger(f"pipeline.{name}")

    def add_stage(self, stage: PipelineStage[Any, Any]) -> "Pipeline[I, O]":
        """Add a processing stage to the pipeline.

        Args:
            stage: Pipeline stage to add

        Returns:
            Self for method chaining
        """
        self.stages.append(stage)
        return self

    def execute(
        self,
        input_data: I,
        context: PipelineContext | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> O:
        """Execute the pipeline on the input data.

        Args:
            input_data: Input data to process
            context: Optional existing pipeline context
            parameters: Optional runtime parameters

        Returns:
            Processed output data

        Raises:
            Exception: If pipeline execution fails
        """
        # Create context if not provided
        if context is None:
            context = PipelineContext(execution_id=str(uuid.uuid4()))

        # Add parameters if provided
        if parameters:
            context.parameters.update(parameters)

        context.status = PipelineStatus.RUNNING
        self.logger.info(f"Starting pipeline: {self.name}")

        # Execute each stage in sequence
        current_data: Any = input_data
        try:
            for stage in self.stages:
                self.logger.info(f"Executing stage: {stage.name}")
                stage_start_time = datetime.now()

                # Process data through this stage
                current_data = stage.process(current_data, context)

                # Record stage execution time
                stage_duration = (datetime.now() - stage_start_time).total_seconds()
                context.add_metric(f"stage.{stage.name}.duration_seconds", stage_duration)

                self.logger.info(f"Completed stage: {stage.name}")

            # Record successful completion
            context.status = PipelineStatus.SUCCEEDED
            context.end_time = datetime.now()
            duration = (context.end_time - context.start_time).total_seconds()
            context.add_metric("pipeline.duration_seconds", duration)

            self.logger.info(f"Pipeline completed successfully in {duration:.2f} seconds")
            return cast(O, current_data)

        except Exception as e:
            # Record failure
            context.status = PipelineStatus.FAILED
            context.end_time = datetime.now()
            context.add_metric("pipeline.error", str(e))

            self.logger.error(f"Pipeline failed: {e!s}", exc_info=True)
            raise
