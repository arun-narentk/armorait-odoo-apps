# -*- coding: utf-8 -*-
"""Product-level forecast lines."""

from odoo import fields, models


class RnInvForecastLine(models.Model):
    """Demand and planning recommendation for one product."""

    _name = 'rn.inv.forecast.line'
    _description = 'Inventory Forecast Line'
    _order = 'forecast_qty desc, id'

    run_id = fields.Many2one('rn.inv.forecast.run', required=True, ondelete='cascade', index=True)
    product_id = fields.Many2one('product.product', required=True, index=True)
    product_tmpl_id = fields.Many2one(related='product_id.product_tmpl_id', store=True)
    categ_id = fields.Many2one(related='product_id.categ_id', store=True)
    warehouse_id = fields.Many2one('stock.warehouse')
    company_id = fields.Many2one(related='run_id.company_id', store=True, index=True)

    history_qty = fields.Float(string='Historical Demand', digits=(16, 2))
    avg_daily_demand = fields.Float(digits=(16, 4))
    forecast_qty = fields.Float(string='Forecast Qty', digits=(16, 2))
    growth_pct = fields.Float(string='Growth %', digits=(16, 2))
    seasonality_factor = fields.Float(default=1.0, digits=(16, 4))

    qty_available = fields.Float(digits=(16, 2))
    incoming_qty = fields.Float(digits=(16, 2))
    outgoing_qty = fields.Float(digits=(16, 2))
    coverage_days = fields.Float(digits=(16, 2))

    safety_stock = fields.Float(digits=(16, 2))
    reorder_point = fields.Float(digits=(16, 2))
    min_qty = fields.Float(digits=(16, 2))
    max_qty = fields.Float(digits=(16, 2))
    recommended_purchase_qty = fields.Float(digits=(16, 2))
    recommended_purchase_date = fields.Date()
    vendor_id = fields.Many2one('res.partner', string='Preferred Vendor')
    lead_time_days = fields.Integer(default=7)

    abc_class = fields.Selection([('A', 'A'), ('B', 'B'), ('C', 'C')])
    xyz_class = fields.Selection([('X', 'X'), ('Y', 'Y'), ('Z', 'Z')])
    fsn_class = fields.Selection([
        ('fast', 'Fast'),
        ('slow', 'Slow'),
        ('non', 'Non Moving'),
    ])
    is_dead_stock = fields.Boolean()
