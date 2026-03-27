
import logfire

from core.agent import agent
from core.deps import AgentDependencies
from core.log import setup_logging
from core.util import clear_temp
from tools.workflow import tools as workflow_tools
from tools.skills import tools as skill_tools
from tools.browser import tools as browser_tools


def main() -> None:
    setup_logging()
    clear_temp()
    deps = AgentDependencies()
    history = []

    while True:
        user_input = input("Chat: ")
        if user_input.lower() in ("exit", "quit"):
            break
        result = agent.run_sync(
            user_input, 
            deps=deps, 
            message_history=history
        )
        
        history = result.all_messages()

        print(f"Agent: {result.output}")