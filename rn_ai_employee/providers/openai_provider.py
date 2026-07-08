# -*- coding: utf-8 -*-
"""OpenAI-compatible provider. Version 1 returns mock responses for install testing."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from .base import BaseAIProvider

_logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    """OpenAI-ready provider. Real HTTP calls will replace mocks in a later version."""

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
        """Return a mock assistant message. Logs prompt metadata only."""
        started = time.perf_counter()
        _logger.info(
            'OpenAIProvider.chat (mock) model=%s messages=%s tools=%s',
            self.model,
            len(messages),
            len(tools or []),
        )
        last_user = next(
            (msg.get('content', '') for msg in reversed(messages) if msg.get('role') == 'user'),
            '',
        )
        response = self._mock_chat_response(last_user, tools or [])
        elapsed = time.perf_counter() - started
        _logger.info('OpenAIProvider.chat (mock) completed in %.3fs', elapsed)
        return response

    def embeddings(self, text: str) -> list[float]:
        """Return a deterministic mock embedding vector."""
        started = time.perf_counter()
        _logger.info('OpenAIProvider.embeddings (mock) chars=%s', len(text or ''))
        if not text:
            return []
        vector = [float((ord(char) % 13) / 13.0) for char in text[:32]]
        elapsed = time.perf_counter() - started
        _logger.info('OpenAIProvider.embeddings (mock) completed in %.3fs', elapsed)
        return vector

    def tool_call(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Return a mock tool call based on simple keyword routing."""
        started = time.perf_counter()
        _logger.info(
            'OpenAIProvider.tool_call (mock) model=%s tools=%s',
            self.model,
            len(tools),
        )
        last_user = next(
            (msg.get('content', '') for msg in reversed(messages) if msg.get('role') == 'user'),
            '',
        )
        response = self._mock_tool_call_response(last_user, tools)
        elapsed = time.perf_counter() - started
        _logger.info('OpenAIProvider.tool_call (mock) completed in %.3fs', elapsed)
        return response

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
            'AI Employee framework is active (mock mode). '
            f'You asked: "{user_text}". '
        )
        if tool_hint:
            content += f'Available tools: {tool_hint}. '
        content += 'Configure a live provider in a future release for full answers.'
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
        """Route common phrases to registry tool names for framework testing."""
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
            'overdue_invoices': ('overdue', 'unpaid', 'past due'),
            'search_customer': ('customer', 'client', 'partner', 'abc company'),
            'create_quotation': ('quotation', 'quote', 'sales order'),
            'product_stock': ('low stock', 'stock', 'inventory', 'qty'),
            'revenue_analysis': ('revenue', 'sales trend', 'decrease', 'decreased'),
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
        import json

        if tool_name == 'overdue_invoices':
            return json.dumps({'days_overdue': 90, 'limit': 20})
        if tool_name == 'search_customer':
            query = 'ABC' if 'abc' in user_text else ''
            return json.dumps({'query': query, 'limit': 10})
        if tool_name == 'create_quotation':
            return json.dumps({
                'partner_name': 'ABC Company' if 'abc' in user_text else '',
                'product_name': 'pump' if 'pump' in user_text else '',
                'quantity': 500 if '500' in user_text else 1,
            })
        if tool_name == 'product_stock':
            return json.dumps({'max_qty': 10.0, 'limit': 20})
        if tool_name == 'revenue_analysis':
            return json.dumps({'month_offset': 0})
        return json.dumps({})
