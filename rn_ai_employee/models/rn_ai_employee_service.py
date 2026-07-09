# -*- coding: utf-8 -*-
"""Orchestration: intent -> tool -> explanation -> action cards."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from odoo import _, api, models
from odoo.exceptions import UserError

from ..services.provider_factory import get_provider, llm_enabled

_logger = logging.getLogger(__name__)


class AiEmployeeService(models.AbstractModel):
    _name = 'rn.ai.employee.service'
    _description = 'AI Employee Orchestration Service'

    @api.model
    def process_chat_message(self, chat, user_text: str) -> None:
        """Route the user question through rules, optional LLM, then tools."""
        started = time.perf_counter()
        user_text = (user_text or '').strip()
        if not user_text:
            raise UserError(_('Message cannot be empty.'))

        self._ensure_enabled()
        self._create_message(chat, 'user', user_text)
        _logger.info('AI Employee prompt chat=%s user=%s', chat.id, self.env.user.login)

        tool_name, arguments = self._resolve_tool(chat, user_text)
        if not tool_name:
            self._reply_with_guidance(chat, user_text)
        else:
            self._run_tool_pipeline(chat, tool_name, arguments, user_text)

        elapsed = time.perf_counter() - started
        _logger.info('AI Employee processed chat=%s in %.3fs', chat.id, elapsed)

    @api.model
    def ensure_system_message(self, chat) -> None:
        if chat.message_ids.filtered(lambda msg: msg.role == 'system'):
            return
        content = _(
            'You are AI Employee for Odoo. I answer everyday business questions using '
            'live company data. Pick a suggested question or ask in your own words.'
        )
        self._create_message(chat, 'system', content)

    @api.model
    def _ensure_enabled(self) -> None:
        enabled = self.env['ir.config_parameter'].get_param('rn_ai_employee.enabled', 'False') == 'True'
        if not enabled:
            raise UserError(_('AI Employee is disabled. Enable it under AI Employee > Settings.'))

    @api.model
    def _resolve_tool(self, chat, user_text: str) -> tuple[str | None, dict[str, Any]]:
        """Try rule-based intent first, then optional LLM tool routing."""
        tool_name, arguments = self.env['rn.ai.employee.intent'].detect(user_text)
        if tool_name:
            return tool_name, arguments
        if llm_enabled(self.env):
            return self._detect_with_llm(chat, user_text)
        return None, {}

    @api.model
    def _detect_with_llm(self, chat, user_text: str) -> tuple[str | None, dict[str, Any]]:
        """Use the configured provider to map natural language to a registered tool."""
        try:
            provider = get_provider(self.env)
            tools = self.env['rn.ai.employee.tool'].get_openai_definitions()
            if not tools:
                return None, {}
            messages = self._build_llm_messages(chat)
            response = provider.tool_call(messages, tools)
            return self._parse_tool_call_response(response)
        except Exception:
            _logger.exception('AI Employee LLM routing failed for chat=%s', chat.id)
            return None, {}

    @api.model
    def _build_llm_messages(self, chat) -> list[dict[str, Any]]:
        """Serialize recent chat history for the provider."""
        messages = [{
            'role': 'system',
            'content': (
                'You are AI Employee for Odoo. Choose exactly one registered tool to answer '
                'the latest user question. Use tool arguments that match the user request. '
                'Do not invent records or data.'
            ),
        }]
        history = chat.message_ids.filtered(
            lambda msg: msg.role in ('user', 'assistant')
        ).sorted('create_date')[-8:]
        for message in history:
            if message.role == 'assistant' and not message.content:
                continue
            messages.append({
                'role': message.role,
                'content': message.content or message.headline or '',
            })
        return messages

    @api.model
    def _parse_tool_call_response(self, response: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
        """Extract tool name and arguments from an OpenAI-style completion payload."""
        choices = response.get('choices') or []
        if not choices:
            return None, {}
        message = choices[0].get('message') or {}
        tool_calls = message.get('tool_calls') or []
        if not tool_calls:
            return None, {}
        function = tool_calls[0].get('function') or {}
        tool_name = function.get('name')
        raw_args = function.get('arguments') or '{}'
        try:
            arguments = json.loads(raw_args) if isinstance(raw_args, str) else dict(raw_args or {})
        except json.JSONDecodeError:
            _logger.warning('Invalid tool arguments from provider: %s', raw_args)
            arguments = {}
        if not tool_name:
            return None, {}
        active = self.env['rn.ai.employee.tool'].search([
            ('model_name', '=', tool_name),
            ('active', '=', True),
        ], limit=1)
        if not active:
            return None, {}
        return tool_name, arguments

    @api.model
    def _run_tool_pipeline(
        self,
        chat,
        tool_name: str,
        arguments: dict[str, Any],
        user_text: str,
    ) -> None:
        tool_started = time.perf_counter()
        result = self.env['rn.ai.employee.tool'].execute_by_name(tool_name, arguments)
        _logger.info(
            'AI Employee tool=%s finished in %.3fs',
            tool_name,
            time.perf_counter() - tool_started,
        )
        self._create_tool_message(chat, tool_name, arguments, result)

        explanation = self.env['rn.ai.employee.explainer'].explain(tool_name, result)
        headline = result.get('headline') if isinstance(result, dict) else None
        assistant_message = self._create_assistant_message(chat, explanation, headline=headline)
        if isinstance(result, dict) and not result.get('error'):
            self.env['rn.ai.employee.message.action'].create_from_tool_result(assistant_message, result)

    @api.model
    def _reply_with_guidance(self, chat, user_text: str) -> None:
        suggestions = self.env['rn.ai.employee.suggestion'].search([('active', '=', True)], limit=6)
        labels = '\n'.join(f'- {item.name}' for item in suggestions)
        content = _(
            'I can help with everyday business questions such as:\n%(suggestions)s\n\n'
            'Try one of the suggested questions above or rephrase your request.'
        ) % {'suggestions': labels or '- Show overdue invoices'}
        self._create_assistant_message(chat, content, headline=_('What would you like to know?'))

    @api.model
    def _create_message(self, chat, role: str, content: str, headline: str | None = None):
        return self.env['rn.ai.employee.message'].create({
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
        self.env['rn.ai.employee.message'].create({
            'chat_id': chat.id,
            'role': 'tool',
            'content': json.dumps(arguments, default=str),
            'tool_name': tool_name,
            'tool_result': json.dumps(result, indent=2, default=str),
        })
