# -*- coding: utf-8 -*-
"""Pending write actions that require explicit user confirmation."""

from __future__ import annotations

import json
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AiEmployeePendingAction(models.Model):
    _name = 'rn.ai.employee.pending.action'
    _description = 'AI Copilot Pending Action'
    _order = 'create_date desc, id desc'

    name = fields.Char(compute='_compute_name', store=True)
    chat_id = fields.Many2one('rn.ai.employee.chat', required=True, ondelete='cascade', index=True)
    user_id = fields.Many2one(
        related='chat_id.user_id',
        store=True,
        index=True,
    )
    company_id = fields.Many2one(
        related='chat_id.company_id',
        store=True,
        index=True,
    )
    tool_name = fields.Char(required=True)
    arguments = fields.Text(default='{}')
    state = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled'),
            ('expired', 'Expired'),
        ],
        default='pending',
        required=True,
        index=True,
    )
    summary = fields.Text()
    message_id = fields.Many2one('rn.ai.employee.message', ondelete='set null')

    @api.depends('tool_name', 'state')
    def _compute_name(self):
        for pending in self:
            pending.name = f'{pending.tool_name} ({pending.state})'

    @api.model
    def create_pending(self, chat, tool_name: str, arguments: dict, summary: str) -> 'AiEmployeePendingAction':
        return self.create({
            'chat_id': chat.id,
            'tool_name': tool_name,
            'arguments': json.dumps(arguments or {}, default=str),
            'summary': summary,
            'state': 'pending',
        })

    def get_arguments(self) -> dict:
        self.ensure_one()
        try:
            return json.loads(self.arguments or '{}')
        except json.JSONDecodeError:
            return {}

    def action_confirm(self):
        """Execute the pending tool after user confirmation."""
        self.ensure_one()
        if self.state != 'pending':
            raise UserError(_('This action is no longer pending confirmation.'))
        if self.chat_id.user_id != self.env.user and not self.env.user.has_group(
            'rn_ai_employee.group_rn_ai_employee_manager'
        ):
            raise UserError(_('You can only confirm your own AI Copilot actions.'))

        service = self.env['rn.ai.employee.service']
        result = service.execute_confirmed_action(self)
        self.state = 'confirmed'
        return result

    def action_cancel(self):
        self.ensure_one()
        if self.state != 'pending':
            return True
        self.state = 'cancelled'
        self.env['rn.ai.employee.audit.log'].log_execution(
            tool_name=self.tool_name,
            arguments=self.get_arguments(),
            result={'error': 'Cancelled by user', 'summary': _('Action cancelled.')},
            chat=self.chat_id,
            pending_action=self,
            confirmed=False,
            result_state='cancelled',
        )
        self.env['rn.ai.employee.message'].create({
            'chat_id': self.chat_id.id,
            'role': 'assistant',
            'headline': _('Action cancelled'),
            'content': _('The pending action was cancelled. No changes were made.'),
        })
        return True
