# -*- coding: utf-8 -*-
"""Previous vendor purchase price on purchase order lines."""

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    previous_vendor_price = fields.Monetary(
        string='Previous Vendor Price',
        compute='_compute_previous_vendor_price',
        currency_field='currency_id',
        help='Last purchase price paid to this vendor for this product.',
    )
    previous_vendor_price_date = fields.Datetime(
        string='Previous Vendor Price Date',
        compute='_compute_previous_vendor_price',
        help='Confirmation/order date of the previous purchase used for the price.',
    )
    previous_vendor_order_id = fields.Many2one(
        'purchase.order',
        string='Previous Vendor Order',
        compute='_compute_previous_vendor_price',
        help='Confirmed purchase order that provided the previous vendor price.',
    )

    @api.depends(
        'product_id',
        'product_uom_id',
        'currency_id',
        'order_id.partner_id',
        'order_id.partner_id.commercial_partner_id',
        'order_id.company_id',
        'order_id.currency_id',
        'display_type',
    )
    def _compute_previous_vendor_price(self):
        for line in self:
            line.previous_vendor_price = 0.0
            line.previous_vendor_price_date = False
            line.previous_vendor_order_id = False

        candidates = self.filtered(
            lambda line: not line.display_type
            and line.product_id
            and line.order_id.partner_id
            and line.order_id.company_id
        )
        if not candidates:
            return

        previous_map = candidates._rn_get_previous_vendor_price_map()
        for line in candidates:
            previous_line = previous_map.get(line._rn_previous_vendor_price_key())
            if not previous_line:
                continue
            previous_order = previous_line.order_id
            line.previous_vendor_price = line._rn_convert_previous_vendor_price(previous_line)
            line.previous_vendor_order_id = previous_order
            line.previous_vendor_price_date = (
                previous_order.date_approve or previous_order.date_order
            )

    def _rn_previous_vendor_price_key(self):
        self.ensure_one()
        return (
            self.product_id.id,
            self.order_id.partner_id.commercial_partner_id.id,
            self.order_id.company_id.id,
        )

    def _rn_get_previous_vendor_price_map(self):
        """Return {(product_id, commercial_id, company_id): purchase.order.line}."""
        commercial_partners = self.mapped('order_id.partner_id.commercial_partner_id')
        company_ids = self.mapped('order_id.company_id').ids
        product_ids = self.mapped('product_id').ids
        exclude_order_ids = self.mapped('order_id').ids

        partner_ids = self.env['res.partner'].search([
            ('id', 'child_of', commercial_partners.ids),
        ]).ids

        # Odoo 19 confirmed POs use state 'purchase' (no separate 'done' state).
        # Keep 'done' for databases that still have legacy rows.
        previous_orders = self.env['purchase.order'].search(
            [
                ('state', 'in', ('purchase', 'done')),
                ('company_id', 'in', company_ids),
                ('partner_id', 'in', partner_ids),
                ('order_line.product_id', 'in', product_ids),
                ('id', 'not in', exclude_order_ids or [0]),
            ],
            order='date_approve desc, date_order desc, id desc',
        )

        best_by_key = {}
        for order in previous_orders:
            commercial_id = order.partner_id.commercial_partner_id.id
            company_id = order.company_id.id
            for order_line in order.order_line:
                if order_line.display_type or not order_line.product_id:
                    continue
                if order_line.product_id.id not in product_ids:
                    continue
                key = (order_line.product_id.id, commercial_id, company_id)
                if key not in best_by_key:
                    best_by_key[key] = order_line
        return best_by_key

    def _rn_convert_previous_vendor_price(self, previous_line):
        """Convert historical price into current line UoM and order currency."""
        self.ensure_one()
        price = previous_line.price_unit

        # UoM: convert unit price from previous UoM into current line UoM.
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
