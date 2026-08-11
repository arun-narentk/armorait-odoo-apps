# -*- coding: utf-8 -*-
"""Refresh product last purchase info when POs are confirmed or cancelled."""

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        result = super().button_confirm()
        products = self.mapped('order_line.product_id')
        if products:
            # Recompute in each order company context.
            for order in self:
                order_products = order.order_line.mapped('product_id')
                if order_products:
                    order_products.with_company(order.company_id)._rn_recompute_last_purchase_info()
        return result

    def button_cancel(self):
        products_by_company = {}
        for order in self:
            products = order.order_line.mapped('product_id')
            if products:
                products_by_company.setdefault(order.company_id, self.env['product.product'])
                products_by_company[order.company_id] |= products
        result = super().button_cancel()
        for company, products in products_by_company.items():
            products.with_company(company)._rn_recompute_last_purchase_info()
        return result
