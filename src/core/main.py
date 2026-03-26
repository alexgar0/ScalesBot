
from core.agent import agent
from tools import workflow 

def main():
    result = agent.run_sync("Can you list files inside your workflow directory? Root folder")
    print(result.output)