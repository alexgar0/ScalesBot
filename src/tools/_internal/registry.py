import asyncio
from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, cast
from functools import wraps

import logfire
from pydantic import BaseModel
from pydantic_ai import Agent

F = TypeVar("F", bound=Callable[..., Any])


class ToolRegistry:
    """Registry for tools"""
    _tools: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def _add(
        cls, func: Callable[..., Any], name: str, is_plain: bool, is_async: bool
    ) -> None:
        cls._tools[name] = {"func": func, "is_plain": is_plain, "is_async": is_async}

    @classmethod
    def apply_to_agent(cls, agent: Agent[Any, Any]) -> None:
        """Applies all registered tools to an agent"""
        applied_tools: List[str] = []
        for name, meta in cls._tools.items():
            func = meta["func"]
            tool_name = meta.get("override_name", name)

            if meta["is_plain"]:
                agent.tool_plain(name=tool_name)(func)
            else:
                agent.tool(name=tool_name)(func)
            applied_tools.append(name)

        logfire.info(f"Loaded {len(applied_tools)} tools")

    @classmethod
    def list_tools(cls) -> List[str]:
        return list(cls._tools.keys())


def tool(name: Optional[str] = None, plain: bool = False) -> Callable[[F], F]:
    """Decorator for registering a tool"""

    def decorator(func: F) -> F:
        tool_name = name or func.__name__
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                return await func(*args, **kwargs)

            async_wrapper.__tool_name__ = tool_name  # type: ignore[attr-defined]
            async_wrapper.__tool_plain__ = plain  # type: ignore[attr-defined]
            async_wrapper.__original_func__ = func  # type: ignore[attr-defined]
            wrapper = cast(F, async_wrapper)
        else:

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                return func(*args, **kwargs)

            sync_wrapper.__tool_name__ = tool_name  # type: ignore[attr-defined]
            sync_wrapper.__tool_plain__ = plain  # type: ignore[attr-defined]
            sync_wrapper.__original_func__ = func  # type: ignore[attr-defined]
            wrapper = cast(F, sync_wrapper)

        ToolRegistry._add(wrapper, tool_name, plain, is_async)
        return wrapper

    return decorator


class DependencyRegistry:
    """Registry for toolset dependencies"""
    _registered_deps: List[Type[BaseModel]] = []

    @classmethod
    def register(cls, dep_class: Type[BaseModel]) -> None:
        """Registers a toolset dependency type"""
        cls._registered_deps.append(dep_class)

    @classmethod
    def get_combined_deps_type(cls) -> Type[BaseModel]:
        """
        Creates a dynamic class AgentDependencies,
        inherits from all registered Deps models.
        """
        if not cls._registered_deps:
            return BaseModel

        cls._validate_fields()
        bases = tuple(cls._registered_deps)
        return type("AgentDependencies", bases, {})

    @classmethod
    def _validate_fields(cls) -> None:
        """Checks, if there are no conflicting fields in deps"""
        used_fields: Set[str] = set()
        for dep_class in cls._registered_deps:
            if not hasattr(dep_class, "model_fields"):
                continue

            for field_name in dep_class.model_fields:
                if field_name in used_fields:
                    raise ValueError(
                        f"Field name collision: '{field_name}' is defined in multiple dependency classes. "
                        f"Rename it to avoid conflicts."
                    )
                used_fields.add(field_name)
