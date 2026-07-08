# -*- coding: utf-8 -*-

from odoo import api, fields, models


class DeadStockLog(models.Model):
    _name = 'dead.stock.log'
    _description = 'Dead Stock Log / Snapshot'
    _order = 'create_date desc'

    product_id = fields.Many2one('product.product', string='Product', ondelete='cascade', index=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    dead_stock_status = fields.Selection([
        ('healthy', 'Healthy'),
        ('slow', 'Slow Moving'),
        ('dead', 'Dead Stock'),
    ], string='Status')
    dead_stock_days = fields.Integer(string='Days Without Movement')
    capital_locked = fields.Float(string='Capital Locked', digits='Product Price')
    note = fields.Char(string='Note')
