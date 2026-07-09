# -*- coding: utf-8 -*-
"""Instagram Direct Messages via Meta Graph API."""

from __future__ import annotations

from typing import Any

from odoo import _

from .base import BaseChannelConnector
from .meta_graph import MetaGraphClient
from .simulation import SimulationConnector


class InstagramDmConnector(BaseChannelConnector):
    technical_name = 'instagram_dm'

    def send_text(self, connector, conversation, text: str) -> dict[str, Any]:
        if connector.simulation_mode:
            return SimulationConnector().send_text(connector, conversation, text)
        page_id = connector.page_id or connector.instagram_account_id
        if not page_id:
            return {'status': 'failed', 'error': _('Missing Instagram account ID.')}
        client = MetaGraphClient(connector)
        return client.send_text_message(
            conversation.external_contact_id,
            text,
            page_id,
        )

    def normalize_inbound(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        if payload.get('object') != 'instagram':
            if payload.get('from') or payload.get('text'):
                return SimulationConnector().normalize_inbound(payload)
            return []
        return MetaGraphClient.normalize_messaging_events(payload)
