# -*- coding: utf-8 -*-
"""Orchestration: intent, memory, confirmation, audit, tools, explanations."""

from __future__ import annotations

import json
import logging
import time
from datetime import timedelta
from typing import Any

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..services.memory_service import get_memory_service
from ..services.agent_service import get_agent_service
from ..services.provider_factory import get_provider, llm_enabled
from ..tools.registry import get_tool_class

_logger = logging.getLogger(__name__)

PRODUCT_NAME = 'AI Copilot for Odoo'


class AiEmployeeService(models.AbstractModel):
    _name = 'rn.ai.employee.service'
    _description = 'AI Copilot Orchestration Service'

    @api.model
    def process_chat_message(self, chat, user_text: str) -> None:
        """Route the user question through rules, memory, optional LLM, then tools."""
        started = time.perf_counter()
        user_text = (user_text or '').strip()
        if not user_text:
            raise UserError(_('Message cannot be empty.'))

        self._ensure_enabled()
        self._create_message(chat, 'user', user_text)
        _logger.info('AI Copilot prompt chat=%s user=%s', chat.id, self.env.user.login)

        tool_name, arguments = self._resolve_tool(chat, user_text)
        if not tool_name:
            self._reply_with_guidance(chat, user_text)
        elif self._requires_confirmation(tool_name):
            self._queue_pending_action(chat, tool_name, arguments, user_text)
        else:
            self._run_tool_pipeline(chat, tool_name, arguments, user_text)

        elapsed = time.perf_counter() - started
        _logger.info('AI Copilot processed chat=%s in %.3fs', chat.id, elapsed)

    @api.model
    def execute_confirmed_action(self, pending_action):
        """Run a pending write action after the user confirms it."""
        arguments = pending_action.get_arguments()
        chat = pending_action.chat_id
        tool_name = pending_action.tool_name
        result = self.env['rn.ai.employee.tool'].execute_by_name(tool_name, arguments)
        self.env['rn.ai.employee.audit.log'].log_execution(
            tool_name=tool_name,
            arguments=arguments,
            result=result,
            chat=chat,
            pending_action=pending_action,
            confirmed=True,
            result_state='error' if isinstance(result, dict) and result.get('error') else 'success',
        )
        self._create_tool_message(chat, tool_name, arguments, result)
        get_memory_service(self.env).remember_tool_result(chat, tool_name, result)
        explanation = self.env['rn.ai.employee.explainer'].explain(tool_name, result)
        headline = result.get('headline') if isinstance(result, dict) else None
        assistant_message = self._create_assistant_message(chat, explanation, headline=headline)
        if isinstance(result, dict) and not result.get('error'):
            self.env['rn.ai.employee.message.action'].create_from_tool_result(assistant_message, result)
        return True

    @api.model
    def ensure_system_message(self, chat) -> None:
        if chat.message_ids.filtered(lambda msg: msg.role == 'system'):
            return
        agent = get_agent_service(self.env).get_chat_agent(chat)
        content = get_agent_service(self.env).build_system_prompt(agent, PRODUCT_NAME)
        self._create_message(chat, 'system', content)

    @api.model
    def generate_morning_briefing(self, user=None, company=None):
        """Build a proactive executive briefing for one user."""
        user = user or self.env.user
        company = company or user.company_id
        env = self.env(user=user.id)

        lines = [_('Good morning %(name)s.') % {'name': user.name}, '']
        currency = company.currency_id.name

        Move = env['account.move']
        SaleOrder = env['sale.order']
        PurchaseOrder = env['purchase.order']

        today = fields.Date.today()
        month_start = today.replace(day=1)
        prev_month_end = month_start - timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)

        current_revenue = sum(Move.search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', month_start),
            ('invoice_date', '<=', today),
            ('company_id', '=', company.id),
        ]).mapped('amount_total'))
        previous_revenue = sum(Move.search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', prev_month_start),
            ('invoice_date', '<=', prev_month_end),
            ('company_id', '=', company.id),
        ]).mapped('amount_total'))

        if previous_revenue:
            change = ((current_revenue - previous_revenue) / previous_revenue) * 100.0
            direction = _('up') if change >= 0 else _('down')
            lines.append(
                _('Revenue this month: %(amount).2f %(currency)s (%(change).1f%% %(direction)s vs last month).') % {
                    'amount': current_revenue,
                    'currency': currency,
                    'change': abs(change),
                    'direction': direction,
                }
            )
        else:
            lines.append(
                _('Revenue this month: %(amount).2f %(currency)s.') % {
                    'amount': current_revenue,
                    'currency': currency,
                }
            )

        overdue = Move.search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('invoice_date_due', '<', today),
            ('company_id', '=', company.id),
        ])
        pending_amount = sum(overdue.mapped('amount_residual'))
        lines.append(
            _('Collections: %(amount).2f %(currency)s pending across %(count)s overdue invoice(s).') % {
                'amount': pending_amount,
                'currency': currency,
                'count': len(overdue),
            }
        )

        pending_quotes = SaleOrder.search_count([
            ('state', 'in', ('draft', 'sent')),
            ('company_id', '=', company.id),
        ])
        if pending_quotes:
            lines.append(_('%(count)s quotation(s) are waiting for confirmation.') % {'count': pending_quotes})

        draft_pos = PurchaseOrder.search_count([
            ('state', '=', 'draft'),
            ('company_id', '=', company.id),
        ])
        if draft_pos:
            lines.append(_('%(count)s purchase order(s) require approval.') % {'count': draft_pos})

        lines.extend(['', _('Suggested actions:')])
        if draft_pos:
            lines.append(_('1. Review draft purchase orders'))
        if overdue:
            lines.append(_('2. Send payment reminders to overdue customers'))
        if pending_quotes:
            lines.append(_('3. Follow up on pending quotations'))

        return '\n'.join(lines)

    @api.model
    def cron_morning_briefing(self):
        """Scheduled proactive briefing for managers who opted in."""
        enabled = self.env['ir.config_parameter'].sudo().get_param(
            'rn_ai_employee.morning_briefing_enabled', 'False'
        ) == 'True'
        if not enabled:
            return

        manager_group = self.env.ref('rn_ai_employee.group_rn_ai_employee_manager', raise_if_not_found=False)
        if not manager_group:
            return

        today_label = fields.Date.today().strftime('%Y-%m-%d')
        for user in manager_group.user_ids.filtered(lambda u: u.active):
            company = user.company_id
            if not company:
                continue
            chat_name = f'Morning Briefing {today_label}'
            Chat = self.env['rn.ai.employee.chat'].with_user(user)
            existing = Chat.search([
                ('user_id', '=', user.id),
                ('name', '=', chat_name),
                ('company_id', '=', company.id),
            ], limit=1)
            if existing:
                continue

            briefing = self.with_user(user).generate_morning_briefing(user, company)
            chat = Chat.create({'name': chat_name})
            self.with_user(user).ensure_system_message(chat)
            self.with_user(user)._create_assistant_message(
                chat,
                briefing,
                headline=_('Your morning briefing'),
            )

    @api.model
    def _ensure_enabled(self) -> None:
        enabled = self.env['ir.config_parameter'].get_param('rn_ai_employee.enabled', 'False') == 'True'
        if not enabled:
            raise UserError(_('AI Copilot is disabled. Enable it under AI Copilot > Settings.'))

    @api.model
    def _confirmation_enabled(self) -> bool:
        return self.env['ir.config_parameter'].sudo().get_param(
            'rn_ai_employee.require_write_confirmation', 'True'
        ) == 'True'

    @api.model
    def _requires_confirmation(self, tool_name: str) -> bool:
        if not self._confirmation_enabled():
            return False
        tool_class = get_tool_class(tool_name)
        return bool(tool_class and getattr(tool_class, 'requires_confirmation', False))

    @api.model
    def _resolve_tool(self, chat, user_text: str) -> tuple[str | None, dict[str, Any]]:
        agent_service = get_agent_service(self.env)
        agent = agent_service.get_chat_agent(chat)
        allowed = agent_service.get_allowed_tool_names(agent) if chat.agent_id else None

        memory = get_memory_service(self.env)
        follow_tool, follow_args = memory.resolve_followup_tool(chat, user_text)
        if follow_tool:
            follow_tool = agent_service.filter_tool_name(agent, follow_tool) if chat.agent_id else follow_tool
            if follow_tool:
                return follow_tool, follow_args

        tool_name, arguments = self.env['rn.ai.employee.intent'].detect(
            user_text,
            allowed_tools=allowed,
        )
        if tool_name:
            return tool_name, memory.enrich_arguments(chat, tool_name, arguments, user_text)
        if llm_enabled(self.env):
            tool_name, arguments = self._detect_with_llm(chat, user_text, agent)
            if tool_name:
                return tool_name, memory.enrich_arguments(chat, tool_name, arguments, user_text)
        return None, {}

    @api.model
    def _detect_with_llm(self, chat, user_text: str, agent=None) -> tuple[str | None, dict[str, Any]]:
        try:
            provider = get_provider(self.env)
            agent_service = get_agent_service(self.env)
            if chat.agent_id:
                tools = agent_service.get_openai_definitions(agent)
            else:
                tools = self.env['rn.ai.employee.tool'].get_openai_definitions()
            if not tools:
                return None, {}
            messages = self._build_llm_messages(chat, agent)
            response = provider.tool_call(messages, tools)
            return self._parse_tool_call_response(response, allowed_tools=(
                agent_service.get_allowed_tool_names(agent) if chat.agent_id else None
            ))
        except Exception:
            _logger.exception('AI Copilot LLM routing failed for chat=%s', chat.id)
            return None, {}

    @api.model
    def _build_llm_messages(self, chat, agent=None) -> list[dict[str, Any]]:
        memory_block = get_memory_service(self.env).build_llm_context(chat)
        agent_service = get_agent_service(self.env)
        system_content = agent_service.build_system_prompt(agent, PRODUCT_NAME)
        system_content += (
            '\n\nChoose exactly one registered tool to answer the latest user question. '
            'Use tool arguments that match the user request. Do not invent records or data.'
        )
        if memory_block:
            system_content += '\n\n' + memory_block
        messages = [{'role': 'system', 'content': system_content}]
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
    def _parse_tool_call_response(
        self,
        response: dict[str, Any],
        allowed_tools: set[str] | None = None,
    ) -> tuple[str | None, dict[str, Any]]:
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
        if allowed_tools is not None and tool_name not in allowed_tools:
            return None, {}
        return tool_name, arguments

    @api.model
    def _queue_pending_action(self, chat, tool_name: str, arguments: dict[str, Any], user_text: str) -> None:
        tool_class = get_tool_class(tool_name)
        label = tool_class.name if tool_class else tool_name
        summary = _('Confirm %(tool)s with arguments: %(args)s') % {
            'tool': label,
            'args': json.dumps(arguments, default=str),
        }
        pending = self.env['rn.ai.employee.pending.action'].create_pending(
            chat, tool_name, arguments, summary,
        )
        self.env['rn.ai.employee.audit.log'].log_execution(
            tool_name=tool_name,
            arguments=arguments,
            result={'summary': summary, 'write_action': True},
            chat=chat,
            pending_action=pending,
            confirmed=False,
            result_state='pending',
        )
        content = _(
            'This action will change live business data.\n\n'
            '%(summary)s\n\n'
            'Confirm to proceed or cancel to keep your data unchanged.'
        ) % {'summary': summary}
        assistant_message = self._create_assistant_message(
            chat,
            content,
            headline=_('Confirmation required'),
        )
        pending.message_id = assistant_message.id
        self.env['rn.ai.employee.message.action'].create([
            {
                'message_id': assistant_message.id,
                'label': _('Confirm'),
                'action_type': 'confirm_write',
                'res_model': 'rn.ai.employee.pending.action',
                'res_ids': json.dumps([pending.id]),
                'sequence': 10,
            },
            {
                'message_id': assistant_message.id,
                'label': _('Cancel'),
                'action_type': 'cancel_write',
                'res_model': 'rn.ai.employee.pending.action',
                'res_ids': json.dumps([pending.id]),
                'sequence': 20,
            },
        ])

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
            'AI Copilot tool=%s finished in %.3fs',
            tool_name,
            time.perf_counter() - tool_started,
        )
        self.env['rn.ai.employee.audit.log'].log_execution(
            tool_name=tool_name,
            arguments=arguments,
            result=result,
            chat=chat,
            confirmed=not self._requires_confirmation(tool_name),
            result_state='error' if isinstance(result, dict) and result.get('error') else 'success',
        )
        self._create_tool_message(chat, tool_name, arguments, result)
        get_memory_service(self.env).remember_tool_result(chat, tool_name, result)

        explanation = self.env['rn.ai.employee.explainer'].explain(tool_name, result)
        headline = result.get('headline') if isinstance(result, dict) else None
        assistant_message = self._create_assistant_message(chat, explanation, headline=headline)
        if isinstance(result, dict) and not result.get('error'):
            self.env['rn.ai.employee.message.action'].create_from_tool_result(assistant_message, result)

    @api.model
    def _reply_with_guidance(self, chat, user_text: str) -> None:
        agent = get_agent_service(self.env).get_chat_agent(chat)
        suggestions = get_agent_service(self.env).get_suggestions(agent, limit=6)
        if chat.agent_id and not suggestions:
            content = get_agent_service(self.env).agent_not_allowed_message(agent)
            self._create_assistant_message(chat, content, headline=_('Try another question'))
            return
        labels = '\n'.join(f'- {item.name}' for item in suggestions)
        headline = _('What would you like to know?')
        if chat.agent_id:
            headline = _('%(agent)s is ready') % {'agent': agent.name}
        content = _(
            'I can help with everyday business questions such as:\n%(suggestions)s\n\n'
            'Try one of the suggested questions above or rephrase your request.'
        ) % {'suggestions': labels or '- Show overdue invoices'}
        self._create_assistant_message(chat, content, headline=headline)

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
