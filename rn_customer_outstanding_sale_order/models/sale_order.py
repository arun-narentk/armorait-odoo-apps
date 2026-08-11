# -*- coding: utf-8 -*-
"""Sale Order: customer receivable outstanding amount."""

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    company_currency_id = fields.Many2one(
        related='company_id.currency_id',
        string='Company Currency',
        readonly=True,
    )
    customer_outstanding = fields.Monetary(
        string='Customer Outstanding',
        compute='_compute_customer_outstanding',
        currency_field='company_currency_id',
        help=(
            'Current unpaid receivable balance for this customer '
            '(commercial partner), based on posted accounting entries only.'
        ),
    )
    has_customer_outstanding = fields.Boolean(
        string='Has Customer Outstanding',
        compute='_compute_customer_outstanding',
        help='True when the customer receivable outstanding is greater than zero.',
    )

    @api.depends('partner_id', 'partner_id.commercial_partner_id', 'company_id')
    def _compute_customer_outstanding(self):
        """Read Odoo Total Receivable for the commercial partner in company context.

        Uses partner.credit so residual, reconciliation, credit notes, and
        multi-currency accounting follow standard Odoo semantics.
        """
        for order in self:
            partner = order.partner_id.commercial_partner_id
            if not partner or not order.company_id:
                order.customer_outstanding = 0.0
                order.has_customer_outstanding = False
                continue
            # Same pattern as core partner_credit_warning: credit is group-restricted.
            commercial = partner.with_company(order.company_id).sudo()
            outstanding = commercial.credit or 0.0
            order.customer_outstanding = outstanding
            order.has_customer_outstanding = outstanding > 0.0
