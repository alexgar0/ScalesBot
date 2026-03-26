
from core.agent import agent
from core.deps import AgentDependencies
from tools.workflow import read
from tools.skills import skill_manager

def main() -> None:
    deps = AgentDependencies()
    result = agent.run_sync("What skills do you have?", deps=deps)
    print(result.output)