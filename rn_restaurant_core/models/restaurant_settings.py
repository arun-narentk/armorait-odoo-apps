# -*- coding: utf-8 -*-
"""Company defaults for restaurant suite."""

from odoo import fields, models


class RnRestaurantSettings(models.Model):
    """Global toggles shared by POS / KDS / QR companions."""

    _name = 'rn.restaurant.settings'
    _description = 'Restaurant Settings'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    default_restaurant_id = fields.Many2one('rn.restaurant', string='Default Restaurant')
    enable_table_management = fields.Boolean(default=True)
    enable_kitchen_stations = fields.Boolean(default=True)
    default_preparation_minutes = fields.Integer(default=12)
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )

    _rn_restaurant_settings_company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one restaurant settings row per company.',
    )
