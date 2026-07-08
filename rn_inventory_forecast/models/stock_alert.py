# -*- coding: utf-8 -*-
"""Inventory smart alerts."""

from odoo import fields, models


class RnInvStockAlert(models.Model):
    """Alert for low, over, dead, negative, or aging stock."""

    _name = 'rn.inv.stock.alert'
    _description = 'Inventory Stock Alert'
    _inherit = ['mail.thread']
    _order = 'severity, create_date desc'

    name = fields.Char(required=True, tracking=True)
    alert_type = fields.Selection(
        selection=[
            ('low', 'Low Stock'),
            ('over', 'Overstock'),
            ('dead', 'Dead Stock'),
            ('negative', 'Negative Inventory'),
            ('aging', 'Stock Aging'),
            ('reorder', 'Reorder Reminder'),
        ],
        required=True,
        index=True,
    )
    severity = fields.Selection(
        selection=[('info', 'Info'), ('warning', 'Warning'), ('critical', 'Critical')],
        default='warning',
        index=True,
    )
    product_id = fields.Many2one('product.product', index=True)
    warehouse_id = fields.Many2one('stock.warehouse')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    qty = fields.Float(digits=(16, 2))
    message = fields.Text()
    state = fields.Selection(
        selection=[('open', 'Open'), ('done', 'Done'), ('ignored', 'Ignored')],
        default='open',
        tracking=True,
    )

    def action_mark_done(self):
        self.write({'state': 'done'})
        return True

    def action_ignore(self):
        self.write({'state': 'ignored'})
        return True
