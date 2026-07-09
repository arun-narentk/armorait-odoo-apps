# -*- coding: utf-8 -*-
"""OpenAI-compatible provider with live HTTP and keyword mock fallback."""

from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any

import requests

from .base import BaseAIProvider

_logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    """OpenAI-compatible chat completions with tool calling."""

    DEFAULT_API_URL = 'https://api.openai.com/v1/chat/completions'

    def validate_configuration(self) -> None:
        super().validate_configuration()
        if not self.api_key:
            raise ValueError('API key is not configured.')

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Send a chat completion request."""
        if not self.api_key:
            return self._mock_chat_response(self._last_user_text(messages), tools or [])
        return self._request_completion(messages, tools=tools)

    def embeddings(self, text: str) -> list[float]:
        """Return a deterministic mock embedding vector when live API is unavailable."""
        if not self.api_key:
            if not text:
                return []
            return [float((ord(char) % 13) / 13.0) for char in text[:32]]
        raise NotImplementedError('Embeddings API is not enabled in this release.')

    def tool_call(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Ask the provider to pick and parameterize a registered tool."""
        if not self.api_key:
            return self._mock_tool_call_response(self._last_user_text(messages), tools)
        return self._request_completion(messages, tools=tools, tool_choice='auto')

    def _request_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        started = time.perf_counter()
        payload: dict[str, Any] = {
            'model': self.model,
            'messages': messages,
            'temperature': self.temperature,
        }
        if tools:
            payload['tools'] = tools
            payload['tool_choice'] = tool_choice or 'auto'

        response = requests.post(
            self.api_url or self.DEFAULT_API_URL,
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            },
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        _logger.info(
            'OpenAIProvider completion model=%s messages=%s tools=%s in %.3fs',
            self.model,
            len(messages),
            len(tools or []),
            time.perf_counter() - started,
        )
        return data

    @staticmethod
    def _last_user_text(messages: list[dict[str, Any]]) -> str:
        return next(
            (msg.get('content', '') for msg in reversed(messages) if msg.get('role') == 'user'),
            '',
        )

    def _mock_chat_response(
        self,
        user_text: str,
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build an OpenAI-style payload with a plain assistant reply."""
        tool_hint = ', '.join(
            (tool.get('function') or {}).get('name', '')
            for tool in tools
            if (tool.get('function') or {}).get('name')
        )
        content = (
            'AI Employee is running in rules-only mode. '
            f'You asked: "{user_text}". '
        )
        if tool_hint:
            content += f'Available tools: {tool_hint}. '
        content += 'Add an API key in AI Employee settings to enable LLM routing.'
        return {
            'id': f'chatcmpl-mock-{uuid.uuid4().hex[:12]}',
            'object': 'chat.completion',
            'choices': [{
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': content,
                },
                'finish_reason': 'stop',
            }],
        }

    def _mock_tool_call_response(
        self,
        user_text: str,
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Route common phrases to registry tool names for offline testing."""
        lowered = (user_text or '').lower()
        tool_name = self._guess_tool_name(lowered, tools)
        if not tool_name:
            return self._mock_chat_response(user_text, tools)

        arguments = self._guess_tool_arguments(tool_name, lowered)
        return {
            'id': f'chatcmpl-mock-{uuid.uuid4().hex[:12]}',
            'object': 'chat.completion',
            'choices': [{
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': None,
                    'tool_calls': [{
                        'id': f'call_{uuid.uuid4().hex[:12]}',
                        'type': 'function',
                        'function': {
                            'name': tool_name,
                            'arguments': arguments,
                        },
                    }],
                },
                'finish_reason': 'tool_calls',
            }],
        }

    @staticmethod
    def _guess_tool_name(user_text: str, tools: list[dict[str, Any]]) -> str | None:
        """Map keywords to registered tool technical names."""
        keyword_map = {
            'overdue_invoices': ('overdue invoice', 'unpaid invoice', 'past due'),
            'send_payment_reminders': ('send reminder', 'payment reminder', 'remind customer'),
            'create_quotation': ('create quotation', 'create quote', 'quotation for'),
            'find_customer': ('find customer', 'search customer', 'inactive customer'),
            'low_stock': ('low stock', 'stock issue', 'running low'),
            'revenue_analysis': ('revenue', 'sales trend', 'decrease', 'decreased', 'why did revenue'),
            'today_sales': ('today sales', 'sales today'),
        }
        available = {
            (tool.get('function') or {}).get('name')
            for tool in tools
            if (tool.get('function') or {}).get('name')
        }
        for technical_name, keywords in keyword_map.items():
            if technical_name in available and any(word in user_text for word in keywords):
                return technical_name
        return None

    @staticmethod
    def _guess_tool_arguments(tool_name: str, user_text: str) -> str:
        """Return JSON string arguments for mock tool calls."""
        if tool_name == 'overdue_invoices':
            return json.dumps({'days_overdue': 0, 'limit': 20})
        if tool_name == 'send_payment_reminders':
            return json.dumps({'days_overdue': 0, 'limit': 10})
        if tool_name == 'find_customer':
            query = 'ABC' if 'abc' in user_text else ''
            return json.dumps({'query': query, 'limit': 10})
        if tool_name == 'create_quotation':
            return json.dumps({
                'partner_name': 'ABC Company' if 'abc' in user_text else 'Customer',
                'product_name': 'pump' if 'pump' in user_text else 'Product',
                'quantity': 500 if '500' in user_text else 1,
            })
        if tool_name == 'low_stock':
            return json.dumps({'max_qty': 10.0, 'limit': 20})
        if tool_name == 'revenue_analysis':
            return json.dumps({'month_offset': 0})
        if tool_name == 'today_sales':
            return json.dumps({})
        return json.dumps({})
