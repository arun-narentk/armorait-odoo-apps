# -*- coding: utf-8 -*-
"""ABC / XYZ / FSN analysis batches."""

from odoo import fields, models


class RnInvAnalysis(models.Model):
    """Stored analysis result for a product and period."""

    _name = 'rn.inv.analysis'
    _description = 'Inventory Analysis'
    _order = 'analysis_date desc, id desc'

    name = fields.Char(required=True)
    analysis_type = fields.Selection(
        selection=[
            ('abc', 'ABC'),
            ('xyz', 'XYZ'),
            ('fsn', 'FSN'),
            ('dead', 'Dead Stock'),
        ],
        required=True,
        index=True,
    )
    analysis_date = fields.Date(required=True, default=fields.Date.context_today, index=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    product_id = fields.Many2one('product.product', required=True, index=True)
    warehouse_id = fields.Many2one('stock.warehouse')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    value = fields.Float(digits=(16, 2), help='Usage value or variability score.')
    qty = fields.Float(digits=(16, 2))
    class_code = fields.Char(index=True)
    note = fields.Char()
