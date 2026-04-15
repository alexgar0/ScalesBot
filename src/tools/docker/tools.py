from typing import Dict, Optional

import httpx
from pydantic import HttpUrl
from pydantic_ai import RunContext

from tools._internal.registry import tool
from tools.docker.deps import DockerDeps


@tool()
def run_docker_compose_module(
    ctx: RunContext[DockerDeps],
    module_name: str,
    build: bool
) -> str:
    """Start or recreate services for a specific Docker Compose module.

    - ENVIRONMENT CONSTRAINT: You have NO direct shell or Docker CLI access. All lifecycle actions 
      MUST route through this tool using exact module names. 
      Your workspace directory is NOT containing these modules. You cannot edit, add, or remove them.
    - Always verify module_name exists in the project structure before calling.
    - Prefer build=False for routine starts. Use build=True only when configuration/code changed.
    - After execution, verify state via `get_containers_from_docker_compose_module` and check logs 
      if containers exit unexpectedly.

    Args:
        module_name (str): Exact name of the subdirectory containing the docker-compose.yml. 
                           Must precisely match the folder name in the isolated project root.
        build (bool): If True, forces image rebuild before starting. Use ONLY after Dockerfile, 
                      source code, or dependency changes. False = fast start using cached images.

    Returns:
        str: Success confirmation or detailed error string on failure.
    """
    try:
        ctx.deps.docker_compose_manager.up(
            module_name=module_name, build=build)
    except Exception as e:
        return f"Got an error while running Docker Compose module {module_name}: {e}"

    return f"Docker Compose module {module_name} started successfully"


@tool()
def stop_docker_compose_module(
    ctx: RunContext[DockerDeps],
    module_name: str,
) -> str:
    """Gracefully stop and remove all containers, networks, and default volumes for a module.

    - DESTRUCTIVE ACTION: Removes containers and default anonymous volumes. Data not bound to 
      explicit named/external volumes will be permanently lost.
    - Use when tearing down environments, freeing system resources, or before major structural changes.
    - Idempotent: Safe to call on already-stopped modules (returns success silently).
    - If you only need a quick state refresh, prefer restart_docker_compose_module.
    - Always confirm teardown by calling `get_containers_from_docker_compose_module` afterward.

    Args:
        module_name (str): Exact name of the target module.

    Returns:
        str: Success confirmation or detailed error string on failure.
    """

    try:
        ctx.deps.docker_compose_manager.down(module_name)
    except Exception as e:
        return f"Got an error while stopping Docker Compose module {module_name}: {e}"

    return f"Docker Compose module {module_name} stopped successfully"


@tool()
def restart_docker_compose_module(
    ctx: RunContext[DockerDeps],
    module_name: str,
) -> str:
    """Restart all running containers within a module without rebuilding images or recreating networks.

    - Optimized for recovering from transient crashes, applying runtime environment variables, 
      or refreshing application state.
    - Preserves network topology, IP assignments, and non-default volumes. Faster than stop+start.
    - DOES NOT rebuild images or detect docker-compose.yml changes. Use run_docker_compose_module(build=True) 
      if infrastructure/config files were modified.
    - Always follow up with `get_logs_from_docker_compose_module` to verify healthy initialization.

    Args:
        module_name (str): Exact name of the target module directory.

    Returns:
        str: Success confirmation or detailed error string on failure.
    """
    try:
        ctx.deps.docker_compose_manager.restart(module_name)
    except Exception as e:
        return f"Got an error while restarting Docker Compose module {module_name}: {e}"

    return f"Docker Compose module {module_name} restarted successfully"


@tool()
def get_logs_from_docker_compose_module(
    ctx: RunContext[DockerDeps],
    module_name: str,
    tail: Optional[int]
) -> str:
    """Retrieve stdout/stderr logs from all services in a Docker Compose module.

    - CONTEXT MANAGEMENT: Never omit `tail` unless explicitly debugging a full historical trace. 
      Large log dumps will consume your working memory and degrade reasoning quality.
    - Use to diagnose startup failures, runtime exceptions, dependency timeouts, or port binding issues.
    - Parse output for critical markers: 'ERROR', 'FATAL', 'Exception', 'Traceback', or success indicators 
      like 'Server started', 'Listening on'.
    - If logs are noisy, first call get_containers_from_docker_compose_module to identify the failing 
      service, then re-fetch logs with a smaller `tail` focused on that service (if supported downstream).

    Args:
        module_name (str): Exact name of the target module directory.
        tail (Optional[int]): Number of most recent log lines to fetch per service. 
                              STRONGLY RECOMMENDED: 50-200. Omitting may cause context overflow.

    Returns:
        str: Aggregated log output prefixed by service name and timestamp, or an error string.
    """
    try:
        return ctx.deps.docker_compose_manager.logs(module_name, tail)
    except Exception as e:
        return f"Got an error while getting logs from Docker Compose module {module_name}: {e}"


@tool()
def get_containers_from_docker_compose_module(
    ctx: RunContext[DockerDeps],
    module_name: str,
) -> str:
    """List all containers associated with a module, including status, names, and port mappings.

    - PRIMARY STATE VERIFICATION TOOL: Check the STATE column before/after any lifecycle action.
      Expected healthy state: 'Up X minutes/hours'. Warning states: 'Exited (code N)', 'Restarting', 'dead'.
    - Use PORTS column to verify external accessibility, detect conflicts, or confirm bind mounts.
    - Essential prerequisite before stopping, restarting, or debugging: confirms the environment 
      is in the expected state.
    - Output is concise and token-efficient. Safe to poll frequently during multi-step operations.
    Args:
        module_name (str): Exact name of the target module directory.

    Returns:
        str: Formatted table/list of containers and their current states, or an error string on failure.
    """
    try:
        return ctx.deps.docker_compose_manager.ps(module_name)
    except Exception as e:
        return f"Got an error while getting containers from Docker Compose module {module_name}: {e}"


@tool()
def list_docker_compose_modules(
    ctx: RunContext[DockerDeps]
) -> str:
    """Discover and enumerate all valid Docker Compose modules in the isolated environment.

    - ENVIRONMENT CONSTRAINT: You have NO direct filesystem traversal or shell access. This tool is 
      the ONLY authoritative source for available modules.
    - WORKFLOW PREREQUISITE: ALWAYS invoke this tool at session start or after structural changes 
      before attempting any lifecycle operation (`run`, `stop`, `restart`, `logs`, etc.).
    - EXACT MATCHING REQUIRED: Returned names precisely match the subdirectory names containing 
      `docker-compose.yml`. Pass these strings verbatim as `module_name` to other tools. 
      Do not modify, abbreviate, or guess names.
    - EMPTY STATE: If the response indicates zero modules, halt lifecycle operations and request 
      environment verification from the user/operator.
    - CONTEXT SAFETY: Output is concise and token-efficient. Cache results in memory when orchestrating 
      multi-module workflows to avoid redundant calls.

    Args:
        ctx (RunContext[DockerDeps]): Execution context providing access to the Docker Compose manager.

    Returns:
        str: Formatted list of available module names, empty state notice, or detailed error string.
    """
    try:
        modules = ctx.deps.docker_compose_manager.list_modules()
        if not modules:
            return "No valid Docker Compose modules found in the environment."
        return "Available Docker Compose modules:\n" + "\n".join(f"- {m}" for m in modules)
    except Exception as e:
        return f"Got an error while listing Docker Compose modules: {e}"
