from pydantic import ConfigDict

from tools._internal.base import ToolsetDeps
from tools.docker.manager import DockerComposeManager


class DockerDeps(ToolsetDeps):
    """Dependencies for docker toolset"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    docker_compose_manager: DockerComposeManager = DockerComposeManager()
