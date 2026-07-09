# -*- coding: utf-8 -*-

from odoo import models


class RnJewelleryPricingService(models.AbstractModel):
    _name = 'rn.jewellery.pricing.service'
    _description = 'Jewellery Pricing Service'

    def compute_item_price(self, item_spec_id):
        item = self.env['rn.jewellery.item.spec'].browse(item_spec_id)
        item.ensure_one()
        return {
            'list_price': item.list_price_computed,
            'metal_type': item.metal_type,
            'net_weight': item.net_weight,
            'making_charge': item.making_charge,
        }

    def recommend_price(self, metal_type, net_weight, purity_id, making_charge=0.0, margin_pct=10.0):
        purity = self.env['rn.jewellery.metal.purity'].browse(purity_id)
        rate = self.env['rn.jewellery.metal.rate'].get_latest_rate(metal_type)
        fine = (net_weight or 0.0) * (purity.purity_factor if purity else 1.0)
        metal_value = fine * rate
        base = metal_value + (making_charge or 0.0)
        suggested = round(base * (1 + (margin_pct or 0.0) / 100.0), 2)
        return {
            'metal_value': round(metal_value, 2),
            'suggested_price': suggested,
            'rate_per_gram': rate,
            'note': 'AI pricing suggestion. Verify before billing.',
        }
