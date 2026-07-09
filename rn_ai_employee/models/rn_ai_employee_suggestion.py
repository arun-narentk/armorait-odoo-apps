# -*- coding: utf-8 -*-
"""Suggested business questions shown on new chats."""

from odoo import fields, models


class AiEmployeeSuggestion(models.Model):
    _name = 'rn.ai.employee.suggestion'
    _description = 'AI Copilot Suggested Question'
    _order = 'category, sequence, id'

    name = fields.Char(string='Label', required=True, translate=True)
    question = fields.Char(string='Question', required=True, translate=True)
    tool_name = fields.Char(
        string='Tool',
        help='Technical tool executed when this question is asked.',
    )
    category = fields.Selection(
        selection=[
            ('sales', 'Sales'),
            ('accounting', 'Accounting'),
            ('inventory', 'Inventory'),
            ('crm', 'CRM'),
        ],
        required=True,
        default='sales',
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    def get_tool_arguments(self):
        """Default arguments for direct suggestion routing."""
        self.ensure_one()
        args = {'limit': 20}
        if self.tool_name == 'overdue_invoices':
            args['days_overdue'] = 90
        if self.tool_name == 'find_customer':
            args['inactive_months'] = 6
        if self.tool_name == 'products_not_moved':
            args['days_without_move'] = 90
        return args

    def action_ask_in_chat(self):
        """Ask this question in the chat passed through context."""
        self.ensure_one()
        chat_id = self.env.context.get('active_id') or self.env.context.get('chat_id')
        if chat_id:
            chat = self.env['rn.ai.employee.chat'].browse(chat_id)
        else:
            action = self.env['rn.ai.employee.chat'].action_start_new_chat()
            chat = self.env['rn.ai.employee.chat'].browse(action['res_id'])
        chat.ensure_one()
        self.env['rn.ai.employee.service'].process_chat_message(chat, self.question)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.ai.employee.chat',
            'res_id': chat.id,
            'view_mode': 'form',
            'target': 'current',
        }
