# -*- coding: utf-8 -*-
"""HSN / SAC summary lines for returns."""

from odoo import fields, models


class RnGstHsnLine(models.Model):
    """HSN/SAC aggregated quantities and tax for a return period."""

    _name = 'rn.gst.hsn.line'
    _description = 'GST HSN Line'
    _order = 'hsn_code'

    return_id = fields.Many2one('rn.gst.return', required=True, ondelete='cascade', index=True)
    hsn_code = fields.Char(required=True, index=True)
    description = fields.Char()
    uom = fields.Char(string='UQC')
    quantity = fields.Float(digits=(16, 3))
    taxable_amount = fields.Monetary(currency_field='currency_id')
    tax_rate = fields.Float(digits=(16, 2))
    cgst_amount = fields.Monetary(currency_field='currency_id')
    sgst_amount = fields.Monetary(currency_field='currency_id')
    igst_amount = fields.Monetary(currency_field='currency_id')
    cess_amount = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(related='return_id.currency_id', store=True)
    company_id = fields.Many2one(related='return_id.company_id', store=True)
