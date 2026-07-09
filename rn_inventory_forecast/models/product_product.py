# -*- coding: utf-8 -*-
"""Product extensions for forecast classifications."""

from odoo import fields, models


class ProductProduct(models.Model):
    """Store latest ABC/XYZ/FSN classification on the product."""

    _inherit = 'product.product'

    rn_inv_abc_class = fields.Selection(
        selection=[('A', 'A'), ('B', 'B'), ('C', 'C')],
        string='ABC Class',
        copy=False,
    )
    rn_inv_xyz_class = fields.Selection(
        selection=[('X', 'X'), ('Y', 'Y'), ('Z', 'Z')],
        string='XYZ Class',
        copy=False,
    )
    rn_inv_fsn_class = fields.Selection(
        selection=[
            ('fast', 'Fast'),
            ('slow', 'Slow'),
            ('non', 'Non Moving'),
        ],
        string='FSN Class',
        copy=False,
    )
    rn_inv_is_dead_stock = fields.Boolean(string='Dead Stock', copy=False)
    rn_inv_avg_daily_demand = fields.Float(string='Avg Daily Demand', digits=(16, 4), copy=False)
    rn_inv_safety_stock = fields.Float(string='Safety Stock', digits=(16, 2), copy=False)
    rn_inv_reorder_point = fields.Float(string='Reorder Point', digits=(16, 2), copy=False)
