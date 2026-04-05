import asyncio
from typing import List
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner

import httpx
import logfire
from pydantic_ai import ModelMessage

from core.agent import agent
from core.deps import AgentDependencies
from core.log import setup_logging
from core.util import clear_temp


async def start() -> None:
    console = Console()
    setup_logging(console)

    logfire.info("Starting agent...")
    clear_temp()

    async with httpx.AsyncClient(timeout=20.0) as client:
        deps = AgentDependencies(http_client=client, current_skills={})
        history: List[ModelMessage] = []

        console.print(
            Panel.fit(
                "🐉 Agent ready! Type 'exit' or 'quit' to stop.", style="bold green"
            )
        )

        while True:
            try:
                user_input = console.input("[bold cyan]You:[/bold cyan] ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if user_input.lower() in ("exit", "quit", "/exit"):
                break

            # spinner = Spinner("dots", text="[bold cyan]Agent is thinking...\n[/bold cyan]")

            with Live(
                None,
                console=console,
                transient=True,
                refresh_per_second=10,
                redirect_stdout=True,
                redirect_stderr=True,
            ) as live:
                if hasattr(agent, "run_stream"):
                    async with agent.run_stream(
                        user_input, deps=deps, message_history=history
                    ) as result:
                        live.stop()

                        console.print(
                            "\n\n[bold magenta]Agent:[/bold magenta]", end=" "
                        )
                        buffer = ""
                        async for chunk in result.stream_text(delta=True):
                            buffer += chunk
                            console.print(chunk, end="", style="dim")
                        console.print()

                else:
                    result = await agent.run(
                        user_input, deps=deps, message_history=history
                    )
                    live.stop()
                    console.print(
                        Panel(
                            Markdown(result.output),
                            title="Agent",
                            title_align="left",
                            style="magenta",
                        )
                    )

            history = result.all_messages() if "result" in locals() else history


def main() -> None:
    asyncio.run(start())


if __name__ == "__main__":
    main()
