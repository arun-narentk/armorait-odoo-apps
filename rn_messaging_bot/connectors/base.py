# -*- coding: utf-8 -*-
"""Abstract connector driver for outbound channel delivery."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseChannelConnector(ABC):
    """Minimal connector contract used by the messaging services."""

    technical_name: str = 'base'

    @abstractmethod
    def send_text(self, connector, conversation, text: str) -> dict[str, Any]:
        """Send a text message and return provider metadata."""

    def normalize_inbound(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        """Convert provider webhook payload into normalized inbound dicts."""
        return []
