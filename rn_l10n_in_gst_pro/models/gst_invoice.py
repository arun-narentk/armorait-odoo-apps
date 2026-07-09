# -*- coding: utf-8 -*-
"""GST invoice lines sourced from account moves for return computation."""

from odoo import fields, models


class RnGstInvoiceLine(models.Model):
    """Normalized invoice row used when building GSTR sections."""

    _name = 'rn.gst.invoice.line'
    _description = 'GST Invoice Line'
    _order = 'invoice_date, id'

    return_id = fields.Many2one('rn.gst.return', required=True, ondelete='cascade', index=True)
    move_id = fields.Many2one('account.move', string='Invoice', index=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    partner_gstin = fields.Char(string='GSTIN')
    invoice_number = fields.Char()
    invoice_date = fields.Date()
    section = fields.Selection(
        selection=[
            ('b2b', 'B2B'),
            ('b2cl', 'B2CL'),
            ('b2cs', 'B2CS'),
            ('export', 'Exports'),
            ('sez', 'SEZ'),
            ('nil', 'Nil Rated'),
            ('exempt', 'Exempt'),
            ('non_gst', 'Non GST'),
            ('cdnr', 'CDNR'),
            ('cdnur', 'CDNUR'),
            ('advance', 'Advance Receipts'),
            ('advance_adj', 'Advance Adjustments'),
        ],
        required=True,
        index=True,
    )
    place_of_supply = fields.Char(string='POS')
    state_code = fields.Char()
    reverse_charge = fields.Boolean(default=False)
    hsn_code = fields.Char()
    taxable_amount = fields.Monetary(currency_field='currency_id')
    cgst_amount = fields.Monetary(currency_field='currency_id')
    sgst_amount = fields.Monetary(currency_field='currency_id')
    igst_amount = fields.Monetary(currency_field='currency_id')
    cess_amount = fields.Monetary(currency_field='currency_id')
    tax_rate = fields.Float(digits=(16, 2))
    currency_id = fields.Many2one(
        'res.currency',
        related='return_id.currency_id',
        store=True,
    )
    company_id = fields.Many2one(related='return_id.company_id', store=True, index=True)
