# -*- coding: utf-8 -*-
"""Abstract AI provider interface. External APIs stay behind this layer."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

_logger = logging.getLogger(__name__)


class BaseAIProvider(ABC):
    """Provider-independent contract for chat, embeddings, and tool calls."""

    def __init__(self, api_key: str, model: str, temperature: float = 0.2, api_url: str = ''):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.api_url = api_url

    @abstractmethod
    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Send a chat completion request and return the provider response payload."""

    @abstractmethod
    def embeddings(self, text: str) -> list[float]:
        """Return a vector embedding for the given text."""

    @abstractmethod
    def tool_call(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Ask the provider to pick and parameterize a tool call."""

    def validate_configuration(self) -> None:
        """Raise ValueError when provider settings are incomplete."""
        if not self.model:
            raise ValueError('AI model name is not configured.')
