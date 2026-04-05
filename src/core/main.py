import asyncio
from typing import List

import httpx
from pydantic_ai import ModelMessage
from loguru import logger

from core.agent import agent
from core.deps import AgentDependencies
from core.log import setup_logging
from core.util import clear_temp


async def start() -> None:
    logger.info("Starting agent...")
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
