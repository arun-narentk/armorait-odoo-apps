# -*- coding: utf-8 -*-
"""Simulation connector for tests and demo without live APIs."""

from __future__ import annotations

import logging
from typing import Any

from .base import BaseChannelConnector

_logger = logging.getLogger(__name__)


class SimulationConnector(BaseChannelConnector):
    technical_name = 'simulation'

    def send_text(self, connector, conversation, text: str) -> dict[str, Any]:
        _logger.info(
            'Simulation send connector=%s conversation=%s text=%s',
            connector.id,
            conversation.id,
            text[:80],
        )
        return {'status': 'sent', 'provider': 'simulation'}

    def normalize_inbound(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        if not payload:
            return []
        return [{
            'external_contact_id': payload.get('from') or payload.get('wa_id') or 'sim-contact',
            'contact_name': payload.get('name') or 'Simulation Contact',
            'content': payload.get('text') or payload.get('body') or '',
            'external_message_id': payload.get('message_id'),
            'message_type': 'text',
        }]
