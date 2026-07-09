# -*- coding: utf-8 -*-
"""Restaurant-specific tax helpers for POS/pricing."""

from odoo import fields, models


class RnRestaurantTax(models.Model):
    """Lightweight tax configuration for F&B pricing engines."""

    _name = 'rn.restaurant.tax'
    _description = 'Restaurant Tax'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    restaurant_id = fields.Many2one('rn.restaurant', required=True, ondelete='cascade', index=True)
    amount = fields.Float(string='Rate %', required=True, default=0.0)
    included_in_price = fields.Boolean(
        string='Included in Price',
        help='When set, list price already contains this tax.',
    )
    company_id = fields.Many2one(
        related='restaurant_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Char()
