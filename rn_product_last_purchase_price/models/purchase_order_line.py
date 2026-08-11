# -*- coding: utf-8 -*-
"""Previous / last purchase price comparison on purchase order lines."""

from odoo import _, api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    last_purchase_price = fields.Monetary(
        string='Last Purchase Price',
        compute='_compute_last_purchase_price',
        currency_field='currency_id',
        help=(
            'Previous purchase unit price for this product. '
            'Prefers the same vendor, then falls back to any vendor.'
        ),
    )
    last_purchase_date = fields.Datetime(
        string='Last Purchase Date',
        compute='_compute_last_purchase_price',
    )
    last_purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Last Purchase Order',
        compute='_compute_last_purchase_price',
    )
    last_purchase_vendor_id = fields.Many2one(
        'res.partner',
        string='Last Purchase Vendor',
        compute='_compute_last_purchase_price',
    )
    purchase_price_difference = fields.Monetary(
        string='Price Difference',
        compute='_compute_last_purchase_price',
        currency_field='currency_id',
        help='Current unit price minus last purchase price.',
    )
    purchase_price_difference_percent = fields.Float(
        string='Price Difference %',
        compute='_compute_last_purchase_price',
        digits=(16, 2),
        help='Percentage change vs last purchase price.',
    )
    last_purchase_warning = fields.Char(
        string='Last Purchase Warning',
        compute='_compute_last_purchase_price',
    )
    has_last_purchase_price_increase = fields.Boolean(
        string='Has Last Purchase Price Increase',
        compute='_compute_last_purchase_price',
    )

    @api.depends(
        'product_id',
        'product_uom_id',
        'price_unit',
        'currency_id',
        'display_type',
        'order_id.partner_id',
        'order_id.partner_id.commercial_partner_id',
        'order_id.company_id',
        'order_id.currency_id',
    )
    def _compute_last_purchase_price(self):
        for line in self:
            line.last_purchase_price = 0.0
            line.last_purchase_date = False
            line.last_purchase_order_id = False
            line.last_purchase_vendor_id = False
            line.purchase_price_difference = False
            line.purchase_price_difference_percent = False
            line.last_purchase_warning = False
            line.has_last_purchase_price_increase = False

        candidates = self.filtered(
            lambda line: not line.display_type
            and line.product_id
            and line.order_id.company_id
        )
        if not candidates:
            return

        # Batch by (product, company, vendor commercial, exclude orders) is hard;
        # group by company and resolve per unique product+vendor with a shared cache.
        cache = {}
        for line in candidates:
            previous_line = line._rn_get_previous_purchase_line(cache)
            if not previous_line:
                continue
            previous_order = previous_line.order_id
            converted = line._rn_convert_previous_purchase_price(previous_line)
            line.last_purchase_price = converted
            line.last_purchase_order_id = previous_order
            line.last_purchase_date = previous_order.date_approve or previous_order.date_order
            line.last_purchase_vendor_id = previous_order.partner_id.commercial_partner_id

            difference = line.price_unit - converted
            line.purchase_price_difference = difference
            if converted:
                percent = (difference / converted) * 100.0
            else:
                percent = 0.0 if not difference else 100.0
            line.purchase_price_difference_percent = percent
            line.has_last_purchase_price_increase = difference > 0.0

            if difference > 0.0:
                line.last_purchase_warning = _(
                    'Price increased by %(percent).2f%%'
                ) % {'percent': percent}
            elif difference < 0.0:
                line.last_purchase_warning = _(
                    'Price reduced by %(percent).2f%%'
                ) % {'percent': abs(percent)}

    def _rn_get_previous_purchase_line(self, cache):
        """Vendor-specific last purchase, then fallback to any vendor."""
        self.ensure_one()
        product = self.product_id
        company = self.order_id.company_id
        vendor = self.order_id.partner_id
        exclude_ids = tuple(sorted(self.order_id.ids))

        vendor_key = (
            'vendor',
            product.id,
            company.id,
            vendor.commercial_partner_id.id,
            exclude_ids,
        )
        if vendor_key not in cache:
            cache[vendor_key] = self.env['product.product']._rn_find_last_purchase_line(
                product,
                company,
                vendor=vendor,
                exclude_order_ids=exclude_ids,
            )
        previous = cache[vendor_key]
        if previous:
            return previous

        any_key = ('any', product.id, company.id, exclude_ids)
        if any_key not in cache:
            cache[any_key] = self.env['product.product']._rn_find_last_purchase_line(
                product,
                company,
                vendor=None,
                exclude_order_ids=exclude_ids,
            )
        return cache[any_key]

    def _rn_convert_previous_purchase_price(self, previous_line):
        """Convert historical unit price into current line UoM and currency."""
        self.ensure_one()
        price = previous_line.price_unit
        prev_uom = previous_line.product_uom_id
        curr_uom = self.product_uom_id
        if prev_uom and curr_uom and prev_uom != curr_uom:
            price = prev_uom._compute_price(price, curr_uom)

        previous_order = previous_line.order_id
        from_currency = previous_order.currency_id
        to_currency = self.currency_id or self.order_id.currency_id
        if not from_currency or not to_currency or from_currency == to_currency:
            return price

        conversion_date = fields.Date.to_date(
            previous_order.date_approve
            or previous_order.date_order
            or fields.Datetime.now()
        )
        return from_currency._convert(
            price,
            to_currency,
            self.order_id.company_id,
            conversion_date,
        )
