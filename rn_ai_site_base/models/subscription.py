# -*- coding: utf-8 -*-
"""SaaS subscription and credits."""

from odoo import fields, models


class RnAiSiteSubscription(models.Model):
    """AI site builder SaaS plan."""

    _name = 'rn.ai.site.subscription'
    _description = 'AI Site SaaS Subscription'
    _inherit = ['mail.thread']
    _order = 'date_end desc'

    name = fields.Char(required=True)
    plan = fields.Selection(
        selection=[
            ('starter', 'Starter (1 site)'),
            ('growth', 'Growth (5 sites)'),
            ('agency', 'Agency (25 sites)'),
            ('unlimited', 'Unlimited'),
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
    ai_credits_monthly = fields.Integer(default=500)
    includes_odoo_publish = fields.Boolean(default=True)
    includes_custom_domain = fields.Boolean(default=False)
    state = fields.Selection(
        selection=[
            ('trial', 'Trial'),
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled'),
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
    note = fields.Text()
