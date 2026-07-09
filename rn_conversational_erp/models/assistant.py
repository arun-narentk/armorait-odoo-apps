# -*- coding: utf-8 -*-
"""Domain assistants for routed conversational workflows."""

from odoo import fields, models


class RnConversationalErpAssistant(models.Model):
    _name = 'rn.conversational.erp.assistant'
    _description = 'Conversational ERP Assistant'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    assistant_scope = fields.Selection(
        selection=[
            ('employee', 'Employee AI'),
            ('customer', 'Customer AI'),
            ('executive', 'Executive AI'),
            ('sales', 'Sales Agent'),
            ('finance', 'Finance Agent'),
            ('inventory', 'Inventory Agent'),
            ('operations', 'Operations Agent'),
        ],
        required=True,
        default='employee',
    )
    keyword_hint = fields.Char(help='Comma-separated keywords used for simple routing in Phase 1.')
    welcome_message = fields.Text(required=True)
    sensitive_actions = fields.Boolean(default=False)
