# -*- coding: utf-8 -*-

from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder=False):
        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
        products = self.mapped('product_id').filtered(lambda p: p.type == 'product')
        if products:
            products._recompute_dead_stock_metrics()
        return res
