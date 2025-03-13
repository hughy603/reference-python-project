"""
Enterprise Nexus integration utilities.

This module provides functionality for interacting with Enterprise Nexus repository,
including artifact publishing, dependency resolution, and repository management.
"""

import logging
import os
import tempfile
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

# Handle tomli/tomllib imports for different Python versions
try:
    # Python 3.11+
    import tomllib as tomli
except ImportError:
    try:
        # For older Python versions
        import tomli
    except ImportError:
        # If tomli is not installed, provide fallback or warning
        import warnings

        warnings.warn(
            "tomli or tomllib module not found. Some functionality may be limited. "
            "Install tomli: pip install tomli",
            stacklevel=2,
        )

        # Define a minimal dummy implementation to prevent errors
        class _DummyTomli:
            @staticmethod
            def load(f):
                warnings.warn("tomli not available, returning empty dict", stacklevel=2)
                return {}

        tomli = _DummyTomli()

# Create a logger directly instead of using a potentially non-existent function
logger = logging.getLogger(__name__)


class NexusClient:
    """Client for interacting with Enterprise Nexus Repository Manager."""

    def __init__(
        self,
        repository_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        verify_ssl: bool = True,
    ):
        """
        Initialize the Nexus client.

        Args:
            repository_url: URL to the Nexus repository. Defaults to the URL in pyproject.toml
                or the NEXUS_REPOSITORY_URL environment variable.
            username: Nexus username. Defaults to NEXUS_USERNAME environment variable.
            password: Nexus password. Defaults to NEXUS_PASSWORD environment variable.
            verify_ssl: Whether to verify SSL certificates when connecting to Nexus.
        """
        self.repository_url = repository_url or os.getenv("NEXUS_REPOSITORY_URL")
        if not self.repository_url:
            self.repository_url = self._get_repository_url_from_pyproject()

        self.username = username or os.getenv("NEXUS_USERNAME")
        self.password = password or os.getenv("NEXUS_PASSWORD")
        self.verify_ssl = verify_ssl
        self.config = self._load_config_from_pyproject()

        if not self.repository_url:
            logger.warning("No Nexus repository URL provided or found")

    def _get_repository_url_from_pyproject(self) -> str | None:
        """Extract the repository URL from pyproject.toml if available."""
        try:
            pyproject_path = Path("pyproject.toml")
            if not pyproject_path.exists():
                return None

            with open(pyproject_path, "rb") as f:
                pyproject_data = tomli.load(f)

            # Look for repository URL in tool.poetry.source section
            if "tool" in pyproject_data and "poetry" in pyproject_data["tool"]:
                poetry_config = pyproject_data["tool"]["poetry"]
                if "source" in poetry_config:
                    for source in poetry_config["source"]:
                        if "name" in source and "url" in source and source["name"] == "nexus":
                            return source["url"]

            return None
        except Exception as e:
            logger.warning(f"Error reading pyproject.toml: {e}")
            return None

    def _load_config_from_pyproject(self) -> dict:
        """Load Nexus configuration from pyproject.toml."""
        try:
            pyproject_path = Path("pyproject.toml")
            if not pyproject_path.exists():
                return {}

            with open(pyproject_path, "rb") as f:
                pyproject_data = tomli.load(f)

            # Look for Nexus configuration in tool.nexus section
            if "tool" in pyproject_data and "nexus" in pyproject_data["tool"]:
                return pyproject_data["tool"]["nexus"]
            return {}
        except Exception as e:
            logger.warning(f"Error reading Nexus configuration from pyproject.toml: {e}")
            return {}

    def upload_artifact(
        self,
        file_path: str,
        repository: str,
        group_id: str,
        artifact_id: str,
        version: str,
        packaging: str = "tar.gz",
    ) -> bool:
        """
        Upload an artifact to the Nexus repository.

        Args:
            file_path: Path to the file to upload
            repository: Target repository name
            group_id: Maven group ID (e.g., 'com.company.project')
            artifact_id: Maven artifact ID (e.g., 'my-component')
            version: Version of the artifact
            packaging: Packaging format (default: 'tar.gz')

        Returns:
            True if upload was successful, False otherwise
        """
        if not self.repository_url:
            logger.error("Cannot upload artifact: No repository URL configured")
            return False

        if not self.username or not self.password:
            logger.error("Cannot upload artifact: No authentication credentials provided")
            return False

        url = f"{self.repository_url}/repository/{repository}/{group_id.replace('.', '/')}/{artifact_id}/{version}/{artifact_id}-{version}.{packaging}"

        logger.info(f"Uploading artifact to {url}")

        try:
            with open(file_path, "rb") as file_data:
                response = requests.put(
                    url,
                    data=file_data,
                    auth=HTTPBasicAuth(self.username, self.password),
                    verify=self.verify_ssl,
                    timeout=60,
                )

            if response.status_code in (200, 201):
                logger.info(f"Successfully uploaded {artifact_id}-{version} to Nexus")
                return True
            else:
                logger.error(
                    f"Failed to upload artifact: HTTP {response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"Error uploading artifact to Nexus: {e}")
            return False

    def download_artifact(
        self,
        repository: str,
        group_id: str,
        artifact_id: str,
        version: str,
        packaging: str = "tar.gz",
        destination: str | None = None,
    ) -> str | None:
        """
        Download an artifact from the Nexus repository.

        Args:
            repository: Source repository name
            group_id: Maven group ID (e.g., 'com.company.project')
            artifact_id: Maven artifact ID (e.g., 'my-component')
            version: Version of the artifact
            packaging: Packaging format (default: 'tar.gz')
            destination: Destination directory (default: current directory)

        Returns:
            Path to the downloaded file if successful, None otherwise
        """
        if not self.repository_url:
            logger.error("Cannot download artifact: No repository URL configured")
            return None

        url = f"{self.repository_url}/repository/{repository}/{group_id.replace('.', '/')}/{artifact_id}/{version}/{artifact_id}-{version}.{packaging}"

        auth = None
        if self.username and self.password:
            auth = HTTPBasicAuth(self.username, self.password)

        logger.info(f"Downloading artifact from {url}")

        try:
            response = requests.get(
                url,
                auth=auth,
                verify=self.verify_ssl,
                stream=True,
                timeout=60,
            )

            if response.status_code == 200:
                if destination:
                    os.makedirs(destination, exist_ok=True)
                    output_path = os.path.join(destination, f"{artifact_id}-{version}.{packaging}")
                else:
                    output_path = f"{artifact_id}-{version}.{packaging}"

                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                logger.info(f"Successfully downloaded {artifact_id}-{version} to {output_path}")
                return output_path
            else:
                logger.error(
                    f"Failed to download artifact: HTTP {response.status_code} - {response.text}"
                )
                return None
        except Exception as e:
            logger.error(f"Error downloading artifact from Nexus: {e}")
            return None

    def check_connection(self) -> bool:
        """
        Check if the Nexus repository is accessible.

        Returns:
            bool: True if the repository is accessible, False otherwise
        """
        if not self.repository_url:
            logger.error("Cannot check connection: No repository URL configured")
            return False

        try:
            # Try to access the repository URL
            auth = None
            if self.username and self.password:
                auth = HTTPBasicAuth(self.username, self.password)

            response = requests.get(
                self.repository_url, auth=auth, verify=self.verify_ssl, timeout=10
            )

            if response.status_code == 200:
                logger.info(f"Successfully connected to Nexus repository at {self.repository_url}")
                return True
            else:
                logger.error(f"Failed to connect to Nexus: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error connecting to Nexus repository: {e}")
            return False

    def configure_pip(self) -> bool:
        """
        Configure pip to use the Nexus repository.

        Returns:
            bool: True if configuration was successful, False otherwise
        """
        if not self.repository_url:
            logger.error("Cannot configure pip: No repository URL configured")
            return False

        try:
            # Determine the repository name - default to 'pypi-all' if not specified
            repository_name = "pypi-all"

            # Create pip configuration
            pip_conf_path = create_pip_conf_with_nexus(
                self.repository_url, repository_name, self.username, self.password
            )

            logger.info(f"Created pip configuration at {pip_conf_path}")

            # Set environment variable to use this config
            os.environ["PIP_CONFIG_FILE"] = pip_conf_path
            logger.info(f"Set PIP_CONFIG_FILE environment variable to {pip_conf_path}")

            return True
        except Exception as e:
            logger.error(f"Error configuring pip: {e}")
            return False


def create_pip_conf_with_nexus(
    nexus_url: str,
    repository_name: str = "pypi",
    username: str | None = None,
    password: str | None = None,
) -> str:
    """
    Create a pip.conf file configured to use Nexus as a PyPI repository.

    Args:
        nexus_url: Base URL of the Nexus server
        repository_name: Name of the PyPI repository in Nexus (default: "pypi")
        username: Optional username for authentication
        password: Optional password for authentication

    Returns:
        Path to the created pip.conf file
    """
    # Create a temporary directory for pip.conf
    temp_dir = tempfile.mkdtemp(prefix="pip-nexus-")
    pip_conf_path = os.path.join(temp_dir, "pip.conf")

    # Format the repository URL, including credentials if provided
    repo_url = f"{nexus_url}/repository/{repository_name}/simple"
    if username and password:
        auth_url = f"https://{username}:{password}@{repo_url.replace('https://', '')}"
    else:
        auth_url = repo_url

    # Create pip.conf content
    pip_conf_content = f"""[global]
index-url = {auth_url}
trusted-host = {nexus_url.replace("https://", "").replace("http://", "")}
"""

    # Write the configuration file
    with open(pip_conf_path, "w") as f:
        f.write(pip_conf_content)

    logger.info(f"Created pip.conf with Nexus configuration at {pip_conf_path}")
    return temp_dir
