# -*- coding: utf-8 -*-
"""Pricing rules for rental assets."""

from odoo import fields, models


class RnRentalPricing(models.Model):
    """Flexible pricing strategy attached to an asset or category."""

    _name = 'rn.rental.pricing'
    _description = 'Rental Pricing Rule'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    asset_id = fields.Many2one('rn.rental.asset', ondelete='cascade', index=True)
    category_id = fields.Many2one('rn.rental.category', index=True)
    plan = fields.Selection(
        selection=[
            ('hourly', 'Hourly'),
            ('half_day', 'Half Day'),
            ('daily', 'Daily'),
            ('weekend', 'Weekend'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
            ('seasonal', 'Seasonal'),
            ('holiday', 'Holiday'),
        ],
        required=True,
        default='daily',
    )
    amount = fields.Monetary(currency_field='currency_id', required=True)
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    date_start = fields.Date()
    date_end = fields.Date()
    min_duration = fields.Float(help='Minimum duration in plan units.')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
