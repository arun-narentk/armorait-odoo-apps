# -*- coding: utf-8 -*-
"""Chat message model with action cards."""

from odoo import fields, models


class AiEmployeeMessage(models.Model):
    _name = 'ai.employee.message'
    _description = 'AI Copilot Message'
    _order = 'create_date asc, id asc'

    chat_id = fields.Many2one(
        'ai.employee.chat',
        string='Chat',
        required=True,
        ondelete='cascade',
        index=True,
    )
    role = fields.Selection(
        selection=[
            ('user', 'User'),
            ('assistant', 'Assistant'),
            ('tool', 'Tool'),
            ('system', 'System'),
        ],
        required=True,
        index=True,
    )
    headline = fields.Char(help='Short answer title shown like an insight card.')
    content = fields.Text()
    tool_name = fields.Char(string='Tool')
    tool_result = fields.Text(string='Tool Result')
    action_ids = fields.One2many(
        'ai.employee.message.action',
        'message_id',
        string='Actions',
    )
    company_id = fields.Many2one(
        related='chat_id.company_id',
        store=True,
        index=True,
    )
    user_id = fields.Many2one(
        related='chat_id.user_id',
        store=True,
    )
