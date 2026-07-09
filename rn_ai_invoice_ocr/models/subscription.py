# -*- coding: utf-8 -*-
"""SaaS subscription for invoice OCR."""

from odoo import fields, models


class RnAiInvoiceOcrSubscription(models.Model):
    """OCR SaaS plan with per-document credits."""

    _name = 'rn.ai.invoice.ocr.subscription'
    _description = 'AI Invoice OCR Subscription'
    _inherit = ['mail.thread']
    _order = 'date_end desc'

    name = fields.Char(required=True)
    plan = fields.Selection(
        selection=[
            ('starter', 'Starter (100 docs/mo)'),
            ('professional', 'Professional (500 docs/mo)'),
            ('enterprise', 'Enterprise (Unlimited)'),
        ],
        default='starter',
        required=True,
    )
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    monthly_fee = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    monthly_credits = fields.Integer(default=100)
    state = fields.Selection(
        selection=[
            ('trial', 'Trial'),
            ('active', 'Active'),
            ('expired', 'Expired'),
        ],
        default='trial',
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
