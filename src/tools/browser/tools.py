import subprocess

import logfire
from pydantic_ai import BinaryContent, ModelRetry, RunContext

from core.config import settings
from tools._internal.registry import tool
from tools.skills.deps import SkillDeps


@tool()
def use_browser(ctx: RunContext[SkillDeps], args: str) -> str:
    """Executes raw browser commands using the 'agent-browser' engine.

    IMPORTANT: This is a low-level tool. Do NOT guess arguments or use this directly for user tasks.

    Args:
        args: The command string. Valid formats are ONLY defined inside loaded skills.
    """

    if not ctx.deps.has_skill("agent-browser"):
        return "Error: The 'agent-browser' skill is not loaded. Please call `load_skill('agent-browser')` first to get instructions."

    logfire.info(f"agent-browser {args}")

    cmd_args = args.split(" ")

    try:
        result = subprocess.run(
            ["agent-browser"] + cmd_args,
            capture_output=True,
            text=True,
            check=True,
            cwd=settings.workspace_path,
        )
        return result.stdout

    except subprocess.CalledProcessError as e:
        return f"Error running the command: {e.stderr}"

    except FileNotFoundError:
        return "Error: 'agent-browser' is not installed or not found in PATH."


@tool()
def take_screenshot(ctx: RunContext[SkillDeps]) -> BinaryContent:
    """
    Takes a screenshot of the current browser state.
    Use this to 'see' the page, analyze visual elements, or check for errors.
    Returns the image.
    """
    screenshot_path = "./tmp/last_state.png"
    cmd = ["agent-browser", "screenshot", screenshot_path]
    logfire.info(" ".join(cmd))
    try:
        subprocess.run(
            cmd, check=True, cwd=settings.workspace_path, capture_output=True
        )
    except subprocess.CalledProcessError as e:
        raise ModelRetry(
            f"Failed to take screenshot: {e.stderr}. Check if browser is running."
        )

    full_path = settings.workspace_path / screenshot_path

    with open(full_path, "rb") as f:
        image_data = f.read()

    return BinaryContent(data=image_data, media_type="image/png")
