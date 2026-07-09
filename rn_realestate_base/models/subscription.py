# -*- coding: utf-8 -*-
"""SaaS subscription tracking."""

from odoo import fields, models


class RnRealestateSubscription(models.Model):
    """Track plan tier for real estate SaaS deployments."""

    _name = 'rn.realestate.subscription'
    _description = 'Real Estate SaaS Subscription'
    _inherit = ['mail.thread']
    _order = 'date_end desc'

    name = fields.Char(required=True)
    developer_id = fields.Many2one('rn.realestate.developer', required=True, index=True)
    plan = fields.Selection(
        selection=[
            ('starter', 'Starter'),
            ('growth', 'Growth'),
            ('professional', 'Professional'),
            ('enterprise', 'Enterprise'),
        ],
        default='growth',
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
    max_projects = fields.Integer(default=5)
    max_users = fields.Integer(default=20)
    company_id = fields.Many2one(
        related='developer_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Text()
