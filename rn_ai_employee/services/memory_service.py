# -*- coding: utf-8 -*-
"""Session memory: keeps recent tool context for follow-up questions."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from odoo import fields

_logger = logging.getLogger(__name__)

_MEMORY_VERSION = 1
_FIRST_N_PATTERN = re.compile(
    r'\b(?:first|top)\s+(\d+)\b|'
    r'\b(\d+)\s+(?:customers?|partners?|quotations?|orders?|invoices?|records?)\b',
    re.IGNORECASE,
)
_FOLLOWUP_PHRASES = (
    'email them', 'email those', 'remind them', 'contact them',
    'first three', 'first 3', 'top three', 'follow up', 'follow-up',
    'send email', 'email the', 'message them',
)


def empty_memory() -> dict[str, Any]:
    return {'version': _MEMORY_VERSION, 'sessions': []}


class MemoryService:
    """Lightweight conversational memory stored on the chat record."""

    def __init__(self, env):
        self.env = env

    def load(self, chat) -> dict[str, Any]:
        raw = chat.memory_context or ''
        if not raw:
            return empty_memory()
        try:
            payload = json.loads(raw)
            if isinstance(payload, dict):
                payload.setdefault('version', _MEMORY_VERSION)
                payload.setdefault('sessions', [])
                return payload
        except json.JSONDecodeError:
            _logger.warning('Invalid memory JSON on chat=%s', chat.id)
        return empty_memory()

    def save(self, chat, memory: dict[str, Any]) -> None:
        chat.sudo().write({'memory_context': json.dumps(memory, default=str)})

    def remember_tool_result(self, chat, tool_name: str, result: dict[str, Any]) -> None:
        if not isinstance(result, dict) or result.get('error'):
            return
        memory = self.load(chat)
        entry = {
            'tool_name': tool_name,
            'model': result.get('model'),
            'record_ids': list(result.get('record_ids') or []),
            'headline': result.get('headline') or '',
            'category': result.get('category') or '',
            'at': fields.Datetime.to_string(fields.Datetime.now()),
        }
        sessions = [entry] + [item for item in memory.get('sessions', []) if item.get('tool_name') != tool_name]
        memory['sessions'] = sessions[:5]
        self.save(chat, memory)

    def latest_entry(self, chat, *, model: str | None = None, category: str | None = None) -> dict[str, Any] | None:
        for entry in self.load(chat).get('sessions', []):
            if model and entry.get('model') != model:
                continue
            if category and entry.get('category') != category:
                continue
            if entry.get('record_ids'):
                return entry
        for entry in self.load(chat).get('sessions', []):
            if entry.get('record_ids'):
                return entry
        return None

    def build_llm_context(self, chat) -> str:
        lines = []
        for entry in self.load(chat).get('sessions', [])[:3]:
            ids = entry.get('record_ids') or []
            if not ids:
                continue
            lines.append(
                f"- {entry.get('tool_name')}: {entry.get('headline')} "
                f"({entry.get('model')}, ids={ids[:10]})"
            )
        if not lines:
            return ''
        return 'Recent session context:\n' + '\n'.join(lines)

    def enrich_arguments(self, chat, tool_name: str, arguments: dict[str, Any], user_text: str) -> dict[str, Any]:
        """Inject record ids from memory for follow-up write tools."""
        args = dict(arguments or {})
        normalized = (user_text or '').strip().lower()
        if not any(phrase in normalized for phrase in _FOLLOWUP_PHRASES):
            return args

        if tool_name in ('send_partner_email', 'schedule_activity', 'send_payment_reminders'):
            if args.get('record_ids') or args.get('partner_ids'):
                return args
            entry = self.latest_entry(chat)
            if not entry:
                return args
            limit = self._extract_limit(normalized, default=3)
            record_ids = (entry.get('record_ids') or [])[:limit]
            args['record_ids'] = record_ids
            args['res_model'] = entry.get('model')
            args['from_memory'] = True
        return args

    def resolve_followup_tool(self, chat, user_text: str) -> tuple[str | None, dict[str, Any]]:
        """Map vague follow-ups to a concrete write tool using session memory."""
        normalized = (user_text or '').strip().lower()
        if not any(phrase in normalized for phrase in _FOLLOWUP_PHRASES):
            return None, {}

        entry = self.latest_entry(chat)
        if not entry:
            return None, {}

        limit = self._extract_limit(normalized, default=3)
        record_ids = (entry.get('record_ids') or [])[:limit]
        model = entry.get('model')

        if 'email' in normalized or 'remind' in normalized or 'contact' in normalized:
            if model == 'account.move':
                return 'send_payment_reminders', {
                    'days_overdue': 0,
                    'limit': limit,
                    'record_ids': record_ids,
                    'from_memory': True,
                }
            return 'send_partner_email', {
                'record_ids': record_ids,
                'res_model': model,
                'from_memory': True,
            }
        if 'activity' in normalized or 'follow' in normalized:
            return 'schedule_activity', {
                'record_ids': record_ids,
                'res_model': model,
                'from_memory': True,
            }
        return None, {}

    @staticmethod
    def _extract_limit(normalized_text: str, default: int = 3) -> int:
        match = _FIRST_N_PATTERN.search(normalized_text)
        if not match:
            return default
        for group in match.groups():
            if group:
                try:
                    return max(1, min(int(group), 25))
                except ValueError:
                    break
        return default


def get_memory_service(env) -> MemoryService:
    return MemoryService(env)
