# -*- coding: utf-8 -*-
"""Menu catalog helpers and price calculation."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnRestaurantMenuService(models.AbstractModel):
    _name = 'rn.restaurant.menu.service'
    _description = 'Restaurant Menu Service'

    def compute_price_with_tax(self, item, qty=1.0):
        item.ensure_one()
        qty = float(qty or 1.0)
        base = float(item.list_price or 0.0) * qty
        tax_total = 0.0
        for tax in item.tax_ids.filtered('active'):
            if tax.included_in_price:
                continue
            tax_total += base * (float(tax.amount or 0.0) / 100.0)
        return {
            'unit_price': item.list_price,
            'qty': qty,
            'untaxed': base,
            'tax': tax_total,
            'total': base + tax_total,
        }

    def available_items(self, restaurant, channel='dine_in'):
        domain = [
            ('restaurant_id', '=', restaurant.id),
            ('active', '=', True),
            ('state', '=', 'available'),
        ]
        field_map = {
            'dine_in': 'available_dine_in',
            'takeaway': 'available_takeaway',
            'delivery': 'available_delivery',
            'online': 'available_online',
        }
        flag = field_map.get(channel)
        if flag:
            domain.append((flag, '=', True))
        return self.env['rn.restaurant.menu.item'].search(domain, order='sequence, name')
