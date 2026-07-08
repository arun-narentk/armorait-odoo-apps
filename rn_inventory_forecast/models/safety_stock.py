# -*- coding: utf-8 -*-
"""Safety stock recommendations."""

from odoo import fields, models


class RnInvSafetyStock(models.Model):
    """Computed safety stock for a product/warehouse."""

    _name = 'rn.inv.safety.stock'
    _description = 'Safety Stock Recommendation'
    _order = 'safety_qty desc'

    name = fields.Char(required=True)
    product_id = fields.Many2one('product.product', required=True, index=True)
    warehouse_id = fields.Many2one('stock.warehouse')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    avg_daily_demand = fields.Float(digits=(16, 4))
    demand_stddev = fields.Float(digits=(16, 4))
    lead_time_days = fields.Integer(default=7)
    service_level = fields.Float(default=0.95, digits=(16, 4))
    safety_qty = fields.Float(digits=(16, 2))
    reorder_point = fields.Float(digits=(16, 2))
    min_qty = fields.Float(digits=(16, 2))
    max_qty = fields.Float(digits=(16, 2))
    computation_date = fields.Datetime(default=fields.Datetime.now)
