# -*- coding: utf-8 -*-
"""Central registry mapping technical tool names to Python classes."""

from __future__ import annotations

from typing import Type

from .base import BaseAITool

TOOL_REGISTRY: dict[str, Type[BaseAITool]] = {}


def register_tool(cls: Type[BaseAITool]) -> Type[BaseAITool]:
    """Decorator to register a tool class by its ``name`` attribute."""
    if not cls.name:
        raise ValueError(f'Tool class {cls.__name__} must define a name.')
    TOOL_REGISTRY[cls.name] = cls
    return cls


def get_tool_class(technical_name: str) -> Type[BaseAITool] | None:
    """Return the Python class for a technical tool name."""
    return TOOL_REGISTRY.get(technical_name)


def get_all_tool_classes() -> list[Type[BaseAITool]]:
    """Return all registered tool classes."""
    return list(TOOL_REGISTRY.values())
