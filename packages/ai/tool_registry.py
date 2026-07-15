"""Tool Registry — auto-discovers agent modules and registers their public functions as tools."""

import importlib
import inspect
from typing import Any, Optional, Callable

from ai.tool_calling import ToolRegistry, ToolDefinition
from shared.utils.logger import logger


def _infer_type_name(annotation) -> str:
    if annotation is inspect.Parameter.empty:
        return "string"
    name = getattr(annotation, "__name__", str(annotation)).lower()
    type_map = {
        "str": "string",
        "int": "integer",
        "float": "number",
        "bool": "boolean",
        "dict": "object",
        "list": "array",
        "any": "string",
        "optional": "string",
        "none": "string",
    }
    return type_map.get(name, "string")


def _infer_parameter_schema(func: Callable) -> dict[str, Any]:
    sig = inspect.signature(func)
    properties: dict[str, dict[str, Any]] = {}
    required: list[str] = []

    for param_name, param in sig.parameters.items():
        if param_name in ("self", "cls"):
            continue

        prop: dict[str, Any] = {
            "type": _infer_type_name(param.annotation),
            "description": f"Parameter '{param_name}' for {func.__name__}",
        }

        default_is_empty = param.default is inspect.Parameter.empty
        if not default_is_empty:
            prop["default"] = param.default
        else:
            if param_name != "kwargs":
                required.append(param_name)

        properties[param_name] = prop

    schema: dict[str, Any] = {
        "type": "object",
        "properties": properties,
    }
    if required:
        schema["required"] = required
    return schema


def _get_public_functions(module) -> dict[str, Callable]:
    funcs: dict[str, Callable] = {}
    for name in dir(module):
        if name.startswith("_"):
            continue
        obj = getattr(module, name)
        if inspect.iscoroutinefunction(obj) or inspect.isfunction(obj):
            if inspect.getmodule(obj) == module:
                funcs[name] = obj
    return funcs


def discover_agent_tools(registry: Optional[ToolRegistry] = None) -> ToolRegistry:
    reg = registry or ToolRegistry()
    agent_module_names = [
        "task_agent",
        "memory_agent",
        "learning_agent",
        "opportunity_agent",
        "briefing_agent",
        "weekly_review_agent",
        "sleep_agent",
        "nudge_agent",
        "roadmap_agent",
        "opportunity_matching_agent",
        "skill_agent",
    ]

    registered_count = 0
    for mod_name in agent_module_names:
        try:
            module = importlib.import_module(f"ai.agents.{mod_name}")
        except ImportError as e:
            logger.warn("Could not import agent module for tool discovery", module=mod_name, error=str(e))
            continue

        funcs = _get_public_functions(module)
        for func_name, func in funcs.items():
            handler_path = f"ai.agents.{mod_name}.{func_name}"
            sig = inspect.signature(func)
            params = _infer_parameter_schema(func)
            param_list = list(sig.parameters.keys())
            user_id_param = "user_id" in param_list

            description_lines: list[str] = []
            doc = inspect.getdoc(func)
            if doc:
                description_lines.append(doc.strip().split("\n")[0][:200])
            else:
                description_lines.append(f"Execute {func_name} from {mod_name}")

            permissions = ["user"] if user_id_param else ["system"]
            first_param = next(
                (p for p in param_list if p not in ("self", "cls")),
                None,
            )
            handler_first_param = first_param or ""

            description = " ".join(description_lines)
            timeout = 60 if func_name in ("generate_briefing", "generate_weekly_review") else 30

            tool = ToolDefinition(
                name=func_name,
                description=description,
                parameters=params,
                handler=handler_path,
                required_permissions=permissions,
                timeout=timeout,
                audit=True,
            )

            try:
                reg.register(tool)
                registered_count += 1
            except ValueError:
                logger.debug("Tool already registered, skipping", name=func_name)

    reg.loaded = True
    logger.info(
        "Tool auto-discovery complete",
        registered=registered_count,
        total=reg.count(),
    )
    return reg


def discover_and_register_all() -> ToolRegistry:
    """Convenience function that discovers and returns the singleton ToolRegistry."""
    registry = ToolRegistry()
    if not registry.loaded:
        discover_agent_tools(registry)
    return registry


def get_registry() -> ToolRegistry:
    """Get the singleton ToolRegistry, auto-discovering if needed."""
    registry = ToolRegistry()
    if not registry.loaded:
        discover_agent_tools(registry)
    return registry
