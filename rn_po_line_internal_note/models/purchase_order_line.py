# -*- coding: utf-8 -*-
"""Purchase order line internal note (buyer-only)."""

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    internal_note = fields.Text(
        string='Internal Note',
        help=(
            'Internal note for this purchase order line. '
            'This information is for internal use only and is not shared with the vendor.'
        ),
        copy=False,
    )
