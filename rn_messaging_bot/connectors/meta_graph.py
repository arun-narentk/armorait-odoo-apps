# -*- coding: utf-8 -*-
"""Shared Meta Graph API helpers for Messenger and Instagram."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

from odoo import _

_logger = logging.getLogger(__name__)


class MetaGraphClient:
    """Minimal HTTP client for Meta messaging endpoints."""

    def __init__(self, connector):
        self.connector = connector
        self.base_url = (connector.api_url or 'https://graph.facebook.com').rstrip('/')
        self.version = connector.api_version or 'v21.0'

    def _request(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.connector.access_token:
            return {'status': 'failed', 'error': _('Missing access token.')}
        url = f'{self.base_url}/{self.version}/{path}'
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {self.connector.access_token}',
                'Content-Type': 'application/json',
            },
            method='POST',
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = json.loads(response.read().decode('utf-8'))
            return {'status': 'sent', 'response': body}
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode('utf-8', errors='replace')
            _logger.warning('Meta Graph send failed: %s', error_body)
            return {'status': 'failed', 'error': error_body}
        except urllib.error.URLError as exc:
            _logger.warning('Meta Graph network error: %s', exc)
            return {'status': 'failed', 'error': str(exc)}

    def send_text_message(self, recipient_id: str, text: str, page_id: str) -> dict[str, Any]:
        payload = {
            'recipient': {'id': recipient_id},
            'messaging_type': 'RESPONSE',
            'message': {'text': text},
        }
        result = self._request(f'{page_id}/messages', payload)
        if result.get('status') == 'sent':
            result['provider'] = 'meta_graph'
        return result

    @staticmethod
    def normalize_messaging_events(payload: dict[str, Any]) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = []
        for entry in payload.get('entry', []):
            for event in entry.get('messaging', []):
                sender_id = event.get('sender', {}).get('id', '')
                message = event.get('message', {})
                if not message:
                    continue
                text_body = message.get('text', '')
                if not text_body and message.get('quick_reply'):
                    text_body = message['quick_reply'].get('payload', '')
                messages.append({
                    'external_contact_id': sender_id,
                    'contact_name': sender_id,
                    'content': text_body,
                    'external_message_id': message.get('mid'),
                    'message_type': 'text',
                })
        return messages
