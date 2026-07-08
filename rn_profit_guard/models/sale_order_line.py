# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import float_round


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    real_margin = fields.Float(
        string='Margin %',
        compute='_compute_margin',
        store=True,
        digits=(5, 2),
        help='(Price - Cost) / Price × 100.',
    )
    margin_status = fields.Selection(
        [
            ('safe', 'Safe'),
            ('warning', 'Warning'),
            ('danger', 'Danger'),
        ],
        string='Margin Status',
        compute='_compute_margin',
        store=True,
        index=True,
    )
    cost_price = fields.Float(
        string='Cost',
        compute='_compute_cost_price',
        store=True,
        digits='Product Price',
    )

    @api.depends('product_id', 'product_id.standard_price', 'product_uom_qty', 'price_subtotal', 'price_unit')
    def _compute_cost_price(self):
        for line in self:
            if line.product_id and line.product_uom_qty:
                line.cost_price = line.product_id.standard_price * line.product_uom_qty
            else:
                line.cost_price = 0.0

    @api.depends('price_unit', 'product_id', 'product_id.standard_price', 'cost_price', 'price_subtotal')
    def _compute_margin(self):
        ICP = self.env['ir.config_parameter'].sudo()
        block_pct = float(ICP.get_param('rn_profit_guard.margin_block_pct', 10))
        warning_pct = float(ICP.get_param('rn_profit_guard.margin_warning_pct', 20))
        safe_pct = float(ICP.get_param('rn_profit_guard.margin_safe_pct', 20))
        for line in self:
            if not line.price_unit or line.display_type:
                line.real_margin = 0.0
                line.margin_status = 'safe'
                continue
            cost = line.product_id and line.product_id.standard_price or 0.0
            if line.price_unit <= 0:
                line.real_margin = 0.0
                line.margin_status = 'danger'
                continue
            margin = (line.price_unit - cost) / line.price_unit * 100.0
            line.real_margin = float_round(margin, precision_digits=2)
            if margin < block_pct:
                line.margin_status = 'danger'
            elif margin < warning_pct:
                line.margin_status = 'warning'
            else:
                line.margin_status = 'safe'
