# -*- coding: utf-8 -*-
"""Settings bridge."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_ocr_auto_extract = fields.Boolean(
        related='company_id.invoice_ocr_auto_extract',
        readonly=False,
    )
    invoice_ocr_enable_gst = fields.Boolean(
        related='company_id.invoice_ocr_enable_gst',
        readonly=False,
    )
    invoice_ocr_duplicate_check = fields.Boolean(
        related='company_id.invoice_ocr_duplicate_check',
        readonly=False,
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    invoice_ocr_auto_extract = fields.Boolean(default=True)
    invoice_ocr_enable_gst = fields.Boolean(default=True)
    invoice_ocr_duplicate_check = fields.Boolean(default=True)
