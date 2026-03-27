from datetime import datetime

from pydantic_ai import RunContext

from core.agent import agent

@agent.tool_plain
def get_local_time() -> str:
    """
    Gets the local time.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")