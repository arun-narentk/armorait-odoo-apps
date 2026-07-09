# -*- coding: utf-8 -*-
"""Meta WhatsApp Cloud API connector."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

from odoo import _

from .base import BaseChannelConnector
from .simulation import SimulationConnector

_logger = logging.getLogger(__name__)


class WhatsappCloudConnector(BaseChannelConnector):
    technical_name = 'whatsapp_cloud'

    def send_text(self, connector, conversation, text: str) -> dict[str, Any]:
        if connector.simulation_mode:
            return SimulationConnector().send_text(connector, conversation, text)
        if not connector.access_token or not connector.phone_number_id:
            return {'status': 'failed', 'error': _('Missing WhatsApp credentials.')}
        url = (
            f"{connector.api_url.rstrip('/')}/{connector.api_version}/"
            f"{connector.phone_number_id}/messages"
        )
        payload = {
            'messaging_product': 'whatsapp',
            'to': conversation.external_contact_id,
            'type': 'text',
            'text': {'body': text},
        }
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {connector.access_token}',
                'Content-Type': 'application/json',
            },
            method='POST',
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = json.loads(response.read().decode('utf-8'))
            return {'status': 'sent', 'provider': 'whatsapp_cloud', 'response': body}
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode('utf-8', errors='replace')
            _logger.warning('WhatsApp send failed: %s', error_body)
            return {'status': 'failed', 'error': error_body}
        except urllib.error.URLError as exc:
            _logger.warning('WhatsApp network error: %s', exc)
            return {'status': 'failed', 'error': str(exc)}

    def normalize_inbound(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = []
        for entry in payload.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                contacts = {
                    item.get('wa_id'): item.get('profile', {}).get('name')
                    for item in value.get('contacts', [])
                }
                for item in value.get('messages', []):
                    text_body = ''
                    if item.get('type') == 'text':
                        text_body = item.get('text', {}).get('body', '')
                    elif item.get('type') == 'button':
                        text_body = item.get('button', {}).get('text', '')
                    else:
                        text_body = item.get('type', '')
                    wa_id = item.get('from', '')
                    messages.append({
                        'external_contact_id': wa_id,
                        'contact_name': contacts.get(wa_id) or wa_id,
                        'content': text_body,
                        'external_message_id': item.get('id'),
                        'message_type': item.get('type', 'text') if item.get('type') != 'button' else 'button',
                    })
        if not messages and (payload.get('from') or payload.get('text') or payload.get('body')):
            return SimulationConnector().normalize_inbound(payload)
        return messages
