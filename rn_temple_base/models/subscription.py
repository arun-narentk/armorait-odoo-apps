# -*- coding: utf-8 -*-
"""SaaS subscription tracking for hosted temple deployments."""

from odoo import fields, models


class RnTempleSubscription(models.Model):
    """Track plan tier and renewal for temple SaaS customers."""

    _name = 'rn.temple.subscription'
    _description = 'Temple SaaS Subscription'
    _inherit = ['mail.thread']
    _order = 'date_end desc'

    name = fields.Char(required=True)
    temple_id = fields.Many2one('rn.temple.temple', required=True, index=True)
    plan = fields.Selection(
        selection=[
            ('starter', 'Starter'),
            ('standard', 'Standard'),
            ('premium', 'Premium'),
            ('enterprise', 'Enterprise'),
        ],
        default='standard',
        required=True,
    )
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    monthly_fee = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
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
    max_branches = fields.Integer(default=1)
    max_users = fields.Integer(default=10)
    company_id = fields.Many2one(
        related='temple_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Text()
