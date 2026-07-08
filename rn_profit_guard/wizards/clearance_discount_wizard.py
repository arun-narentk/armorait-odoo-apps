# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class ClearanceDiscountWizard(models.TransientModel):
    _name = 'clearance.discount.wizard'
    _description = 'Clearance Discount (Dead Stock)'

    order_id = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete='cascade')
    line_ids = fields.Many2many(
        'sale.order.line',
        string='Lines to Apply Discount',
        help='Select lines (e.g. dead stock products) to apply clearance discount.',
    )
    discount_pct = fields.Float(string='Discount %', digits=(5, 2), default=0)
    min_margin_pct = fields.Float(
        string='Minimum Margin %',
        digits=(5, 2),
        default=0,
        help='Ensure margin does not go below this after discount.',
    )

    def action_apply_clearance(self):
        self.ensure_one()
        for line in self.line_ids:
            if line.display_type or not line.product_id:
                continue
            cost = line.product_id.standard_price
            if cost <= 0:
                continue
            # Apply discount: new price such that margin >= min_margin_pct
            # margin = (price - cost) / price  =>  price = cost / (1 - margin/100)
            min_price = cost / (1.0 - self.min_margin_pct / 100.0) if self.min_margin_pct < 100 else cost
            new_price = line.price_unit * (1.0 - self.discount_pct / 100.0)
            if new_price < min_price:
                new_price = min_price
            line.write({'price_unit': new_price, 'discount': 0})
        return {'type': 'ir.actions.act_window_close'}
