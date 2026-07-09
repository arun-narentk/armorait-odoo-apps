# -*- coding: utf-8 -*-
"""Extracted invoice line items."""

from odoo import fields, models


class RnAiInvoiceScanLine(models.Model):
    """Line item parsed from a supplier invoice."""

    _name = 'rn.ai.invoice.scan.line'
    _description = 'AI Invoice Scan Line'
    _order = 'sequence, id'

    scan_id = fields.Many2one(
        'rn.ai.invoice.scan',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(default=10)
    description = fields.Char(required=True)
    product_id = fields.Many2one('product.product', string='Matched Product')
    quantity = fields.Float(default=1.0)
    price_unit = fields.Monetary(currency_field='currency_id')
    discount = fields.Float()
    tax_percent = fields.Float(string='Tax %')
    price_subtotal = fields.Monetary(currency_field='currency_id')
    hsn_code = fields.Char(string='HSN/SAC')
    confidence = fields.Float(string='Confidence %')
    currency_id = fields.Many2one(related='scan_id.currency_id')
    company_id = fields.Many2one(related='scan_id.company_id', store=True)
