# -*- coding: utf-8 -*-
"""Learned vendor and product text mappings."""

from odoo import fields, models


class RnAiInvoiceVendorMapping(models.Model):
    """Maps OCR vendor text to Odoo partner for smart learning."""

    _name = 'rn.ai.invoice.vendor.mapping'
    _description = 'Invoice Vendor Mapping'
    _order = 'hit_count desc'

    ocr_text = fields.Char(required=True, index=True)
    partner_id = fields.Many2one('res.partner', required=True, index=True)
    hit_count = fields.Integer(default=1)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    _ocr_partner_company_uniq = models.Constraint(
        'unique(ocr_text, company_id)',
        'This OCR vendor text is already mapped for this company.',
    )


class RnAiInvoiceProductMapping(models.Model):
    """Maps OCR line description to Odoo product."""

    _name = 'rn.ai.invoice.product.mapping'
    _description = 'Invoice Product Mapping'
    _order = 'hit_count desc'

    ocr_text = fields.Char(required=True, index=True)
    product_id = fields.Many2one('product.product', required=True, index=True)
    hit_count = fields.Integer(default=1)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    _ocr_product_company_uniq = models.Constraint(
        'unique(ocr_text, company_id)',
        'This OCR product text is already mapped for this company.',
    )
