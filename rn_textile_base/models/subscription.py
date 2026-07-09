# -*- coding: utf-8 -*-
"""SaaS subscription tracking."""

from odoo import fields, models


class RnTextileSubscription(models.Model):
    """Track plan tier for textile SaaS or AMC deployments."""

    _name = 'rn.textile.subscription'
    _description = 'Textile SaaS Subscription'
    _inherit = ['mail.thread']
    _order = 'date_end desc'

    name = fields.Char(required=True)
    factory_id = fields.Many2one('rn.textile.factory', required=True, index=True)
    plan = fields.Selection(
        selection=[
            ('starter', 'Starter'),
            ('standard', 'Standard'),
            ('professional', 'Professional'),
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
    max_machines = fields.Integer(default=20)
    max_users = fields.Integer(default=25)
    includes_amc = fields.Boolean(string='Includes AMC')
    company_id = fields.Many2one(
        related='factory_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Text()
