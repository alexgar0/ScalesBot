from typing import Any, Callable, Dict, List, Optional, Set, Type
from functools import wraps

from loguru import logger
from pydantic import BaseModel
from pydantic_ai import Agent


class ToolRegistry:
    _tools: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def _add(cls, func: Callable[..., Any], name: str, is_plain: bool) -> None:
        cls._tools[name] = {"func": func, "is_plain": is_plain}

    @classmethod
    def apply_to_agent(cls, agent: Agent[Any, str]) -> None:
        """Applies all registered tools to an agent"""
        applied_tools: List[str] = []
        for name, meta in cls._tools.items():
            func = meta["func"]
            if meta["is_plain"]:
                agent.tool_plain(name=meta.get("override_name", name))(func)
            else:
                agent.tool(name=meta.get("override_name", name))(func)

            applied_tools.append(name)

        logger.info(f"Loaded {len(applied_tools)} tools")

    @classmethod
    def list_tools(cls) -> List[str]:
        return list(cls._tools.keys())


def tool(
    name: Optional[str] = None, plain: bool = False
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for registering a tool"""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        tool_name = name or func.__name__

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        wrapper.__tool_name__ = tool_name  # type: ignore[attr-defined]
        wrapper.__tool_plain__ = plain  # type: ignore[attr-defined]
        wrapper.__original_func__ = func  # type: ignore[attr-defined]

        ToolRegistry._add(wrapper, tool_name, plain)
        return wrapper

    return decorator


class DependencyRegistry:
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