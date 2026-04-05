import httpx
from pydantic import BaseModel, ConfigDict

from tools._internal.base import ToolsetDeps


class RequestsDeps(ToolsetDeps):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    http_client: httpx.AsyncClient
