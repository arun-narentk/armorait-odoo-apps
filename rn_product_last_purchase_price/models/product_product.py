# -*- coding: utf-8 -*-
"""Last purchase info on product variants."""

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    last_purchase_price = fields.Float(
        string='Last Purchase Price',
        digits='Product Price',
        company_dependent=True,
        groups='purchase.group_purchase_user',
        help='Unit price from the latest confirmed purchase order for this product.',
    )
    last_purchase_date = fields.Datetime(
        string='Last Purchase Date',
        company_dependent=True,
        groups='purchase.group_purchase_user',
        help='Confirmation/order date of the latest confirmed purchase.',
    )
    last_purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Last Purchase Order',
        company_dependent=True,
        groups='purchase.group_purchase_user',
        help='Confirmed purchase order used for the last purchase price.',
    )
    last_purchase_vendor_id = fields.Many2one(
        'res.partner',
        string='Last Vendor',
        company_dependent=True,
        groups='purchase.group_purchase_user',
        help='Vendor of the latest confirmed purchase for this product.',
    )

    def _rn_clear_last_purchase_info(self):
        self.write({
            'last_purchase_price': 0.0,
            'last_purchase_date': False,
            'last_purchase_order_id': False,
            'last_purchase_vendor_id': False,
        })

    def _rn_recompute_last_purchase_info(self):
        """Refresh stored last-purchase fields from confirmed PO lines (company-aware)."""
        products = self.exists()
        if not products:
            return

        company = self.env.company
        OrderLine = self.env['purchase.order.line']

        # One search for all products in the current company.
        lines = OrderLine.search([
            ('product_id', 'in', products.ids),
            ('order_id.state', 'in', ('purchase', 'done')),
            ('order_id.company_id', '=', company.id),
            ('display_type', '=', False),
        ])

        # Latest = max(date_approve or date_order, order id, line id).
        ranked = {}
        for line in lines:
            product_id = line.product_id.id
            order = line.order_id
            sort_key = (
                order.date_approve or order.date_order or fields.Datetime.from_string('1970-01-01'),
                order.id,
                line.id,
            )
            current = ranked.get(product_id)
            if not current or sort_key > current[0]:
                ranked[product_id] = (sort_key, line)

        for product in products:
            ranked_line = ranked.get(product.id)
            if not ranked_line:
                product._rn_clear_last_purchase_info()
                continue
            line = ranked_line[1]
            order = line.order_id
            price = product._rn_convert_purchase_line_price_to_cost_currency(line)
            product.write({
                'last_purchase_price': price,
                'last_purchase_date': order.date_approve or order.date_order,
                'last_purchase_order_id': order.id,
                'last_purchase_vendor_id': order.partner_id.commercial_partner_id.id,
            })

    def _rn_convert_purchase_line_price_to_cost_currency(self, purchase_line):
        """Convert PO line unit price into product cost currency and product UoM."""
        self.ensure_one()
        price = purchase_line.price_unit
        prev_uom = purchase_line.product_uom_id
        product_uom = self.uom_id
        if prev_uom and product_uom and prev_uom != product_uom:
            price = prev_uom._compute_price(price, product_uom)

        order = purchase_line.order_id
        from_currency = order.currency_id
        to_currency = self.cost_currency_id or order.company_id.currency_id
        if not from_currency or not to_currency or from_currency == to_currency:
            return price

        conversion_date = fields.Date.to_date(
            order.date_approve or order.date_order or fields.Datetime.now()
        )
        return from_currency._convert(
            price,
            to_currency,
            order.company_id,
            conversion_date,
        )

    @api.model
    def _rn_find_last_purchase_line(
        self,
        product,
        company,
        vendor=None,
        exclude_order_ids=None,
    ):
        """Return the latest confirmed purchase.order.line for a product.

        :param vendor: if set, restrict to that commercial partner's purchases.
        :param exclude_order_ids: PO ids to ignore (usually the current order).
        """
        if not product or not company:
            return self.env['purchase.order.line']

        domain = [
            ('product_id', '=', product.id),
            ('display_type', '=', False),
            ('order_id.state', 'in', ('purchase', 'done')),
            ('order_id.company_id', '=', company.id),
        ]
        if exclude_order_ids:
            domain.append(('order_id', 'not in', list(exclude_order_ids)))

        if vendor:
            commercial = vendor.commercial_partner_id
            partner_ids = self.env['res.partner'].search([
                ('id', 'child_of', commercial.ids),
            ]).ids
            domain.append(('order_id.partner_id', 'in', partner_ids))

        lines = self.env['purchase.order.line'].search(domain)
        if not lines:
            return self.env['purchase.order.line']

        def sort_key(line):
            order = line.order_id
            return (
                order.date_approve or order.date_order or fields.Datetime.from_string('1970-01-01'),
                order.id,
                line.id,
            )

        return max(lines, key=sort_key)
