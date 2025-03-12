FROM python:3.12-slim

# Set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.6.1 \
    HATCH_VERSION=1.9.0

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    make \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install hatch for dependency management
RUN pip install hatch==$HATCH_VERSION

# Copy pyproject.toml
COPY pyproject.toml .
COPY README.md .

# Copy source code
COPY src/ src/
COPY tests/ tests/
COPY scripts/ scripts/

# Create and activate environment
RUN hatch env create

# Install the package
RUN pip install -e .

# Set the entrypoint to use hatch
ENTRYPOINT ["hatch", "run"]

# Default command (can be overridden)
CMD ["python", "-m", "enterprise_data_engineering"]
