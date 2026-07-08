# -*- coding: utf-8 -*-
"""Company rental settings."""

from odoo import fields, models


class RnRentalSettings(models.Model):
    """Defaults for pricing and availability."""

    _name = 'rn.rental.settings'
    _description = 'Rental Settings'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, default='Rental Settings')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    default_plan = fields.Selection(
        selection=[
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='daily',
    )
    default_deposit_pct = fields.Float(default=20.0)
    allow_overlap_block = fields.Boolean(
        default=True,
        help='Block bookings when availability conflicts are found.',
    )
    enable_email = fields.Boolean(default=True)
    timezone = fields.Char(default='UTC')
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one rental settings record per company.',
    )
