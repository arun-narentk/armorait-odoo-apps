# -*- coding: utf-8 -*-
"""Extracted document line items."""

from odoo import fields, models


class RnDocumentIdpLine(models.Model):
    _name = 'rn.document.idp.line'
    _description = 'IDP Document Line'
    _order = 'sequence, id'

    document_id = fields.Many2one(
        'rn.document.idp.document',
        required=True,
        ondelete='cascade',
        index=True,
    )
    company_id = fields.Many2one(related='document_id.company_id', store=True)
    sequence = fields.Integer(default=10)
    description = fields.Char(required=True)
    product_id = fields.Many2one('product.product')
    quantity = fields.Float(default=1.0)
    price_unit = fields.Float()
    tax_percent = fields.Float()
    price_subtotal = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(related='document_id.currency_id')
    hsn_code = fields.Char(string='HSN/SAC')
    confidence = fields.Float()
