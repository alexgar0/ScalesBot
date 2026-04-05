import httpx
from pydantic import ConfigDict

from tools._internal.base import ToolsetDeps


class RequestsDeps(ToolsetDeps):
    """Dependencies for requests toolset"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    http_client: httpx.AsyncClient
