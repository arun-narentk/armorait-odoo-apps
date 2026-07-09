# -*- coding: utf-8 -*-
"""Purchase / replenishment suggestions."""

from odoo import fields, models


class RnInvReorderSuggestion(models.Model):
    """Recommended purchase quantity and date."""

    _name = 'rn.inv.reorder.suggestion'
    _description = 'Reorder Suggestion'
    _inherit = ['mail.thread']
    _order = 'recommended_date, id'

    name = fields.Char(required=True, tracking=True)
    product_id = fields.Many2one('product.product', required=True, index=True, tracking=True)
    warehouse_id = fields.Many2one('stock.warehouse')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    vendor_id = fields.Many2one('res.partner', string='Preferred Vendor')
    qty_to_order = fields.Float(digits=(16, 2), tracking=True)
    recommended_date = fields.Date()
    lead_time_days = fields.Integer(default=7)
    safety_refill = fields.Boolean(string='Safety Stock Refill')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('recommended', 'Recommended'),
            ('ordered', 'Ordered'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ],
        default='recommended',
        tracking=True,
    )
    note = fields.Text()

    def action_mark_ordered(self):
        self.write({'state': 'ordered'})
        return True
