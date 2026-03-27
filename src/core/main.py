import asyncio
from typing import List

import httpx
from pydantic_ai import ModelMessage

from core.agent import agent
from core.deps import AgentDependencies
from core.log import setup_logging
from core.util import clear_temp

from tools.workspace import tools as workspace_tools
from tools.skills import tools as skill_tools
from tools.browser import tools as browser_tools
from tools.requests import tools as requests_tools
from tools.common import tools as common_tools


async def start() -> None:
    setup_logging()
    clear_temp()
    async with httpx.AsyncClient(timeout=20.0) as client:
        deps = AgentDependencies(
            http_client=client,
            current_skills={},
        )
        history: List[ModelMessage] = []
        while True:
            user_input = input("Chat: ")
            if user_input.lower() in ("exit", "quit"):
                break
            result = await agent.run(user_input, deps=deps, message_history=history)

            history = result.all_messages()

            print(f"Agent: {result.output}")


def main() -> None:
    asyncio.run(start())
