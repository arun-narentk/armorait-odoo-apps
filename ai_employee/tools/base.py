# -*- coding: utf-8 -*-
"""Base class for AI Employee tools."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from odoo.api import Environment


class BaseAITool(ABC):
    """One safe, ORM-backed capability exposed to the AI layer."""

    name: str = ''
    description: str = ''

    def __init__(self, env: Environment):
        self.env = env

    @abstractmethod
    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Run the tool with validated arguments and return a JSON-serializable dict."""

    def as_openai_definition(self) -> dict[str, Any]:
        """Return the OpenAI function schema for this tool."""
        return {
            'type': 'function',
            'function': {
                'name': self.name,
                'description': self.description,
                'parameters': self.get_parameters_schema(),
            },
        }

    def get_parameters_schema(self) -> dict[str, Any]:
        """Override in subclasses to describe accepted arguments."""
        return {'type': 'object', 'properties': {}}
