# -*- coding: utf-8 -*-
"""Last confirmed customer sale price on sale order lines."""

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    last_sale_price = fields.Float(
        string='Last Sale Price',
        digits='Product Price',
        compute='_compute_last_sale_price',
        help=(
            'The effective unit price from the customer\'s most recent '
            'confirmed sale of this product.'
        ),
    )

    @api.depends(
        'product_id',
        'product_uom_id',
        'currency_id',
        'display_type',
        'order_id.partner_id',
        'order_id.partner_id.commercial_partner_id',
        'order_id.company_id',
        'order_id.currency_id',
    )
    def _compute_last_sale_price(self):
        for line in self:
            line.last_sale_price = 0.0

        candidates = self.filtered(
            lambda line: not line.display_type
            and line.product_id
            and line.order_id.partner_id
            and line.order_id.company_id
        )
        if not candidates:
            return

        previous_map = candidates._rn_get_last_sale_line_map()
        for line in candidates:
            previous_line = previous_map.get(line._rn_last_sale_price_key())
            if previous_line:
                line.last_sale_price = line._rn_convert_last_sale_price(previous_line)

    def _rn_last_sale_price_key(self):
        self.ensure_one()
        return (
            self.product_id.id,
            self.order_id.partner_id.commercial_partner_id.id,
            self.order_id.company_id.id,
        )

    def _rn_get_last_sale_line_map(self):
        """Return {(product_id, commercial_id, company_id): sale.order.line}.

        One search for all candidate lines. Orders are newest confirmation
        date first; first matching product line per key wins.
        """
        commercial_partners = self.mapped('order_id.partner_id.commercial_partner_id')
        company_ids = self.mapped('order_id.company_id').ids
        product_ids = self.mapped('product_id').ids
        exclude_order_ids = self.mapped('order_id').ids

        partner_ids = self.env['res.partner'].search([
            ('id', 'child_of', commercial_partners.ids),
        ]).ids

        # Odoo 19 confirmed SO state is 'sale'. Keep 'done' for legacy rows.
        # date_order is the confirmation date on confirmed orders.
        previous_orders = self.env['sale.order'].search(
            [
                ('state', 'in', ('sale', 'done')),
                ('company_id', 'in', company_ids),
                ('partner_id', 'in', partner_ids),
                ('order_line.product_id', 'in', product_ids),
                ('id', 'not in', exclude_order_ids or [0]),
            ],
            order='date_order desc, id desc',
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

    def _rn_convert_last_sale_price(self, previous_line):
        """Effective historical unit price in current line UoM and currency."""
        self.ensure_one()
        # What the customer actually paid per unit (after line discount).
        price = previous_line._get_discounted_price()

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
            previous_order.date_order or fields.Datetime.now()
        )
        return from_currency._convert(
            price,
            to_currency,
            self.order_id.company_id,
            conversion_date,
        )
