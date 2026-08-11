# -*- coding: utf-8 -*-
"""Internal note on account.move.line (invoices and bills)."""

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    internal_note = fields.Text(
        string='Internal Note',
        help=(
            'Internal note for this invoice line. '
            'This note is not shown on the customer-facing invoice.'
        ),
        copy=False,
    )
