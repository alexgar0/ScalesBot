from typing import Dict, Optional

import httpx
from pydantic import HttpUrl
from pydantic_ai import RunContext

from tools.registry import tool
from tools.requests.deps import RequestsDeps


@tool()
async def do_http_request(
    ctx: RunContext[RequestsDeps],
    url: HttpUrl,
    method: str,
    json_body: Optional[Dict[str, str]],
) -> str:
    """Does an HTTP request to the specified URL.
    Use this to interact with external APIs or websites.

    Args:
        url: The target URL.
        method: HTTP method (GET, POST, PUT, DELETE, etc.).
        json_body: Optional JSON body for POST/PUT requests.
    """

    client = ctx.deps.http_client

    method = method.upper()

    try:
        response = await client.request(
            method=method,
            url=str(url),
            json=json_body,
            follow_redirects=True,
            timeout=20.0,
        )

        content_type = response.headers.get("content-type", "")

        response_text = response.text
        if len(response_text) > 2000:
            response_text = response_text[:2000] + "\n... [RESPONSE TRUNCATED]"

        result = (
            f"Status Code: {response.status_code}\n"
            f"Content-Type: {content_type}\n"
            f"Response Body:\n{response_text}"
        )

        return result

    except httpx.TimeoutException:
        return "Error: Request timed out."
    except httpx.RequestError as e:
        return f"Error: Network error occurred - {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error - {str(e)}"
