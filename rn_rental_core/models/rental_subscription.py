# -*- coding: utf-8 -*-
"""SaaS / edition tracking for ARMORA Rental."""

from odoo import fields, models


class RnRentalSubscription(models.Model):
    """Tracks which rental edition a company is entitled to."""

    _name = 'rn.rental.subscription'
    _description = 'Rental Subscription'
    _inherit = ['mail.thread']
    _order = 'date_start desc'

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    edition = fields.Selection(
        selection=[
            ('core', 'Core'),
            ('professional', 'Professional'),
            ('suite', 'Full Suite'),
            ('saas', 'SaaS'),
        ],
        default='core',
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('trial', 'Trial'),
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('cancel', 'Cancelled'),
        ],
        default='trial',
        tracking=True,
    )
    date_start = fields.Date(default=fields.Date.context_today)
    date_end = fields.Date()
    max_assets = fields.Integer(default=100)
    note = fields.Text()
