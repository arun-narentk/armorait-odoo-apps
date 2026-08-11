# -*- coding: utf-8 -*-
"""Customer previous selling price on sale order lines."""

from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero, float_round


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    previous_customer_price = fields.Monetary(
        string='Previous Customer Price',
        compute='_compute_previous_customer_price',
        currency_field='currency_id',
        help='Most recent selling price of this product to this customer.',
    )
    previous_customer_order_id = fields.Many2one(
        'sale.order',
        string='Previous Customer Order',
        compute='_compute_previous_customer_price',
        help='Confirmed sale order that provided the previous customer price.',
    )
    previous_customer_order_date = fields.Datetime(
        string='Previous Order Date',
        compute='_compute_previous_customer_price',
        help='Order date of the previous customer order.',
    )
    previous_customer_price_difference = fields.Monetary(
        string='Difference vs Previous Price',
        compute='_compute_previous_customer_price',
        currency_field='currency_id',
        help='Current unit price minus previous customer price. '
             'Positive means the current price is higher.',
    )
    previous_customer_price_percentage = fields.Float(
        string='Difference %',
        compute='_compute_previous_customer_price',
        digits=(16, 2),
        help='Percentage difference vs previous customer price.',
    )

    @api.depends(
        'product_id',
        'price_unit',
        'currency_id',
        'order_id.partner_id',
        'order_id.partner_id.commercial_partner_id',
        'order_id.company_id',
        'order_id.currency_id',
        'order_id.date_order',
        'display_type',
    )
    def _compute_previous_customer_price(self):
        """Batch-load the latest confirmed price per customer/product/company."""
        for line in self:
            line.previous_customer_price = False
            line.previous_customer_order_id = False
            line.previous_customer_order_date = False
            line.previous_customer_price_difference = False
            line.previous_customer_price_percentage = False

        candidates = self.filtered(
            lambda line: not line.display_type
            and line.product_id
            and line.order_id.partner_id
            and line.order_id.company_id
        )
        if not candidates:
            return

        previous_map = candidates._rn_get_previous_customer_price_map()
        for line in candidates:
            key = line._rn_previous_price_key()
            previous_line = previous_map.get(key)
            if not previous_line:
                continue

            previous_order = previous_line.order_id
            converted_price = line._rn_convert_previous_price(previous_line)
            line.previous_customer_price = converted_price
            line.previous_customer_order_id = previous_order
            line.previous_customer_order_date = previous_order.date_order

            if converted_price is False:
                continue

            difference = line.price_unit - converted_price
            line.previous_customer_price_difference = difference
            rounding = line.currency_id.rounding if line.currency_id else 0.01
            if not float_is_zero(converted_price, precision_rounding=rounding):
                line.previous_customer_price_percentage = float_round(
                    (difference / converted_price) * 100.0,
                    precision_digits=2,
                )

    def _rn_previous_price_key(self):
        self.ensure_one()
        return (
            self.product_id.id,
            self.order_id.partner_id.commercial_partner_id.id,
            self.order_id.company_id.id,
        )

    def _rn_get_previous_customer_price_map(self):
        """Return {(product_id, commercial_id, company_id): sale.order.line}."""
        commercial_partners = self.mapped('order_id.partner_id.commercial_partner_id')
        company_ids = self.mapped('order_id.company_id').ids
        product_ids = self.mapped('product_id').ids
        exclude_order_ids = self.mapped('order_id').ids

        partner_ids = self.env['res.partner'].search([
            ('id', 'child_of', commercial_partners.ids),
        ]).ids

        # Odoo 19 confirmed orders use state 'sale' (no separate 'done' state).
        # Keep 'done' in the domain for databases that still have legacy rows.
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
                # First hit wins because orders are newest-first.
                if key not in best_by_key:
                    best_by_key[key] = order_line
        return best_by_key

    def _rn_convert_previous_price(self, previous_line):
        """Convert historical unit price into the current order currency."""
        self.ensure_one()
        previous_order = previous_line.order_id
        from_currency = previous_order.currency_id
        to_currency = self.currency_id or self.order_id.currency_id
        if not from_currency or not to_currency:
            return previous_line.price_unit
        if from_currency == to_currency:
            return previous_line.price_unit

        conversion_date = fields.Date.to_date(
            previous_order.date_order or fields.Datetime.now()
        )
        return from_currency._convert(
            previous_line.price_unit,
            to_currency,
            self.order_id.company_id,
            conversion_date,
        )
