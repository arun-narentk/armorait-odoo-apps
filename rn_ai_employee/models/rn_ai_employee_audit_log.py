# -*- coding: utf-8 -*-
"""Immutable audit trail for every AI tool execution."""

from __future__ import annotations

import json

from odoo import api, fields, models


class AiEmployeeAuditLog(models.Model):
    _name = 'rn.ai.employee.audit.log'
    _description = 'AI Copilot Audit Log'
    _order = 'create_date desc, id desc'

    name = fields.Char(compute='_compute_name', store=True)
    user_id = fields.Many2one('res.users', required=True, index=True, ondelete='restrict')
    company_id = fields.Many2one('res.company', required=True, index=True, ondelete='restrict')
    chat_id = fields.Many2one('rn.ai.employee.chat', index=True, ondelete='set null')
    agent_id = fields.Many2one(
        'rn.ai.employee.agent',
        string='Domain Agent',
        index=True,
        ondelete='set null',
    )
    pending_action_id = fields.Many2one(
        'rn.ai.employee.pending.action',
        index=True,
        ondelete='set null',
    )
    tool_name = fields.Char(required=True, index=True)
    arguments = fields.Text()
    result_state = fields.Selection(
        selection=[
            ('pending', 'Pending Confirmation'),
            ('success', 'Success'),
            ('error', 'Error'),
            ('cancelled', 'Cancelled'),
        ],
        required=True,
        default='success',
        index=True,
    )
    result_summary = fields.Text()
    confirmed = fields.Boolean(default=False)
    write_action = fields.Boolean(default=False, index=True)

    @api.depends('tool_name', 'user_id', 'create_date')
    def _compute_name(self):
        for log in self:
            user = log.user_id.display_name if log.user_id else ''
            when = fields.Datetime.to_string(log.create_date) if log.create_date else ''
            log.name = f'{log.tool_name or "tool"} / {user} / {when}'

    @api.model
    def log_execution(
        self,
        *,
        tool_name: str,
        arguments: dict | None,
        result: dict | None,
        chat=None,
        pending_action=None,
        confirmed: bool = False,
        result_state: str = 'success',
    ):
        summary = ''
        write_action = False
        if isinstance(result, dict):
            summary = result.get('summary') or result.get('headline') or result.get('error') or ''
            write_action = bool(result.get('write_action'))
        return self.create({
            'user_id': self.env.user.id,
            'company_id': self.env.company.id,
            'chat_id': chat.id if chat else False,
            'agent_id': chat.agent_id.id if chat and chat.agent_id else False,
            'pending_action_id': pending_action.id if pending_action else False,
            'tool_name': tool_name,
            'arguments': json.dumps(arguments or {}, default=str),
            'result_state': result_state,
            'result_summary': summary,
            'confirmed': confirmed,
            'write_action': write_action,
        })
