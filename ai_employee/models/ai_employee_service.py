# -*- coding: utf-8 -*-
"""Orchestration: intent -> tool -> explanation -> action cards."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AiEmployeeService(models.AbstractModel):
    _name = 'ai.employee.service'
    _description = 'AI Employee Orchestration Service'

    @api.model
    def process_chat_message(self, chat, user_text: str) -> None:
        """Business-first pipeline without delegating logic to the LLM."""
        started = time.perf_counter()
        user_text = (user_text or '').strip()
        if not user_text:
            raise UserError(_('Message cannot be empty.'))

        self._ensure_enabled()
        self._create_message(chat, 'user', user_text)
        _logger.info('AI Copilot prompt chat=%s user=%s', chat.id, self.env.user.login)

        tool_name, arguments = self.env['ai.employee.intent'].detect(user_text)
        if not tool_name:
            self._reply_with_guidance(chat, user_text)
        else:
            self._run_tool_pipeline(chat, tool_name, arguments, user_text)

        elapsed = time.perf_counter() - started
        _logger.info('AI Copilot processed chat=%s in %.3fs', chat.id, elapsed)

    @api.model
    def ensure_system_message(self, chat) -> None:
        if chat.message_ids.filtered(lambda msg: msg.role == 'system'):
            return
        content = _(
            'You are AI Copilot for Odoo. I answer everyday business questions using '
            'live company data. Pick a suggested question or ask in your own words.'
        )
        self._create_message(chat, 'system', content)

    @api.model
    def _ensure_enabled(self) -> None:
        enabled = self.env['ir.config_parameter'].get_param('ai_employee.enabled', 'False') == 'True'
        if not enabled:
            raise UserError(_('AI Copilot is disabled. Enable it under AI Copilot > Settings.'))

    @api.model
    def _run_tool_pipeline(
        self,
        chat,
        tool_name: str,
        arguments: dict[str, Any],
        user_text: str,
    ) -> None:
        tool_started = time.perf_counter()
        result = self.env['ai.employee.tool'].execute_by_name(tool_name, arguments)
        _logger.info(
            'AI Copilot tool=%s finished in %.3fs',
            tool_name,
            time.perf_counter() - tool_started,
        )
        self._create_tool_message(chat, tool_name, arguments, result)

        explanation = self.env['ai.employee.explainer'].explain(tool_name, result)
        headline = result.get('headline') if isinstance(result, dict) else None
        assistant_message = self._create_assistant_message(chat, explanation, headline=headline)
        if isinstance(result, dict) and not result.get('error'):
            self.env['ai.employee.message.action'].create_from_tool_result(assistant_message, result)

    @api.model
    def _reply_with_guidance(self, chat, user_text: str) -> None:
        suggestions = self.env['ai.employee.suggestion'].search([('active', '=', True)], limit=6)
        labels = '\n'.join(f'- {item.name}' for item in suggestions)
        content = _(
            'I can help with everyday business questions such as:\n%(suggestions)s\n\n'
            'Try one of the suggested questions above or rephrase your request.'
        ) % {'suggestions': labels or '- Show overdue invoices'}
        self._create_assistant_message(chat, content, headline=_('What would you like to know?'))

    @api.model
    def _create_message(self, chat, role: str, content: str, headline: str | None = None):
        return self.env['ai.employee.message'].create({
            'chat_id': chat.id,
            'role': role,
            'content': content,
            'headline': headline,
        })

    @api.model
    def _create_assistant_message(self, chat, content: str, headline: str | None = None):
        return self._create_message(chat, 'assistant', content, headline=headline)

    @api.model
    def _create_tool_message(
        self,
        chat,
        tool_name: str,
        arguments: dict[str, Any],
        result: dict[str, Any],
    ) -> None:
        self.env['ai.employee.message'].create({
            'chat_id': chat.id,
            'role': 'tool',
            'content': json.dumps(arguments, default=str),
            'tool_name': tool_name,
            'tool_result': json.dumps(result, indent=2, default=str),
        })
