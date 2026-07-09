# -*- coding: utf-8 -*-
"""Restaurant bootstrap helpers."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnRestaurantService(models.AbstractModel):
    _name = 'rn.restaurant.service'
    _description = 'Restaurant Service'

    def ensure_defaults(self, restaurant):
        """Create starter payment methods and taxes when empty."""
        restaurant.ensure_one()
        Tax = self.env['rn.restaurant.tax']
        Pay = self.env['rn.restaurant.payment.method']
        if not restaurant.tax_ids:
            Tax.create({
                'name': 'GST 5%',
                'restaurant_id': restaurant.id,
                'amount': 5.0,
            })
        if not restaurant.payment_method_ids:
            for name, mtype, drawer in [
                ('Cash', 'cash', True),
                ('Card', 'card', False),
                ('UPI', 'upi', False),
            ]:
                Pay.create({
                    'name': name,
                    'restaurant_id': restaurant.id,
                    'method_type': mtype,
                    'opens_drawer': drawer,
                })
        _logger.info('Ensured defaults for restaurant %s', restaurant.code)
        return True
