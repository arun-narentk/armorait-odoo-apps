# -*- coding: utf-8 -*-
"""Last purchase info on product templates."""

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    last_purchase_price = fields.Float(
        string='Last Purchase Price',
        digits='Product Price',
        compute='_compute_last_purchase_info',
        groups='purchase.group_purchase_user',
        help='Latest confirmed purchase unit price among this template variants.',
    )
    last_purchase_date = fields.Datetime(
        string='Last Purchase Date',
        compute='_compute_last_purchase_info',
        groups='purchase.group_purchase_user',
    )
    last_purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Last Purchase Order',
        compute='_compute_last_purchase_info',
        groups='purchase.group_purchase_user',
    )
    last_purchase_vendor_id = fields.Many2one(
        'res.partner',
        string='Last Vendor',
        compute='_compute_last_purchase_info',
        groups='purchase.group_purchase_user',
    )

    @api.depends(
        'product_variant_ids',
        'product_variant_ids.last_purchase_price',
        'product_variant_ids.last_purchase_date',
        'product_variant_ids.last_purchase_order_id',
        'product_variant_ids.last_purchase_vendor_id',
    )
    def _compute_last_purchase_info(self):
        for template in self:
            variants = template.product_variant_ids.filtered('last_purchase_order_id')
            if not variants:
                template.last_purchase_price = 0.0
                template.last_purchase_date = False
                template.last_purchase_order_id = False
                template.last_purchase_vendor_id = False
                continue

            def sort_key(product):
                return (
                    product.last_purchase_date or fields.Datetime.from_string('1970-01-01'),
                    product.last_purchase_order_id.id,
                    product.id,
                )

            best = max(variants, key=sort_key)
            template.last_purchase_price = best.last_purchase_price
            template.last_purchase_date = best.last_purchase_date
            template.last_purchase_order_id = best.last_purchase_order_id
            template.last_purchase_vendor_id = best.last_purchase_vendor_id
