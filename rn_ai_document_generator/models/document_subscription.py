# -*- coding: utf-8 -*-
"""SaaS edition tracking for Document Automation."""

from odoo import fields, models


class RnAiDocumentSubscription(models.Model):
    _name = 'rn.ai.document.subscription'
    _description = 'AI Document Subscription'
    _order = 'id desc'

    name = fields.Char(required=True)
    plan = fields.Selection(
        selection=[
            ('marketplace', 'Marketplace'),
            ('professional', 'Professional'),
            ('saas', 'SaaS'),
        ],
        default='marketplace',
        required=True,
    )
    state = fields.Selection(
        selection=[
            ('trial', 'Trial'),
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled'),
        ],
        default='trial',
        required=True,
    )
    list_price = fields.Float(help='Marketplace 59.99 / Professional 99.99 USD')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    date_start = fields.Date()
    date_end = fields.Date()
    note = fields.Text()
