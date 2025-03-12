"""Spark session configuration and creation utilities."""

from dataclasses import dataclass

from pyspark.sql import SparkSession


@dataclass
class SparkConfig:
    """Configuration class for creating a Spark session.

    This class provides a structured way to configure a Spark session with
    common parameters used in enterprise environments.

    Attributes:
        app_name: Name of the Spark application
        master: The Spark master URL (local, yarn, etc.)
        log_level: Spark log level (INFO, WARN, ERROR, etc.)
        configs: Additional configuration parameters
        jars: List of JARs to include
        packages: Maven packages to include
    """

    app_name: str
    master: str = "local[*]"
    log_level: str = "WARN"
    configs: dict[str, str] = None
    jars: list[str] = None
    packages: list[str] = None

    def __post_init__(self) -> None:
        """Initialize default empty collections."""
        if self.configs is None:
            self.configs = {}
        if self.jars is None:
            self.jars = []
        if self.packages is None:
            self.packages = []


def create_spark_session(
    config: SparkConfig | None = None,
    enable_hive: bool = False,
    enable_delta: bool = False,
) -> SparkSession:
    """Create a configured Spark session.

    Args:
        config: SparkConfig object with configuration parameters
        enable_hive: Whether to enable Hive support
        enable_delta: Whether to enable Delta Lake

    Returns:
        Configured SparkSession object

    Examples:
        >>> # Simple local session
        >>> spark = create_spark_session(SparkConfig(app_name="MyApp"))
        >>>
        >>> # More complex configuration
        >>> spark = create_spark_session(
        ...     SparkConfig(
        ...         app_name="DataProcessing",
        ...         master="yarn",
        ...         log_level="INFO",
        ...         configs={
        ...             "spark.sql.adaptive.enabled": "true",
        ...             "spark.sql.shuffle.partitions": "200",
        ...         },
        ...         packages=["org.apache.hadoop:hadoop-aws:3.3.1"],
        ...     ),
        ...     enable_delta=True,
        ... )
    """
    if config is None:
        config = SparkConfig(app_name="DefaultSparkApp")

    # Start with basic builder
    builder = SparkSession.builder.appName(config.app_name)

    # Set master if provided
    if config.master:
        builder = builder.master(config.master)

    # Add additional configuration
    for key, value in config.configs.items():
        builder = builder.config(key, value)

    # Add packages if provided
    if config.packages:
        packages = ",".join(config.packages)
        builder = builder.config("spark.jars.packages", packages)

    # Add JARs if provided
    if config.jars:
        jars = ",".join(config.jars)
        builder = builder.config("spark.jars", jars)

    # Enable Hive support if requested
    if enable_hive:
        builder = builder.enableHiveSupport()

    # Enable Delta Lake if requested
    if enable_delta:
        builder = builder.config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        builder = builder.config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )

    # Create session
    spark = builder.getOrCreate()

    # Set log level
    spark.sparkContext.setLogLevel(config.log_level)

    return spark


def get_default_session(
    app_name: str = "DefaultApp",
    log_level: str = "WARN",
    enable_delta: bool = False,
) -> SparkSession:
    """Get a simple default Spark session for quick development.

    Args:
        app_name: Name of the Spark application
        log_level: Spark log level
        enable_delta: Whether to enable Delta Lake

    Returns:
        SparkSession configured for local development
    """
    # Standard local development configuration
    config = SparkConfig(
        app_name=app_name,
        master="local[*]",
        log_level=log_level,
        configs={
            # Performance tuning for local development
            "spark.sql.adaptive.enabled": "true",
            "spark.sql.adaptive.coalescePartitions.enabled": "true",
            "spark.sql.shuffle.partitions": "10",
            "spark.default.parallelism": "10",
            # Useful for debugging
            "spark.sql.execution.arrow.pyspark.enabled": "true",
        },
    )

    # Add Delta package if requested
    if enable_delta:
        config.packages.append("io.delta:delta-core_2.12:2.4.0")

    return create_spark_session(config, enable_delta=enable_delta)
