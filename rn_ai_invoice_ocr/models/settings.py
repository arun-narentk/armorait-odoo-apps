# -*- coding: utf-8 -*-
"""OCR settings and credits."""

from odoo import fields, models


class RnAiInvoiceOcrSettings(models.Model):
    """Per-company AI Invoice OCR configuration."""

    _name = 'rn.ai.invoice.ocr.settings'
    _description = 'AI Invoice OCR Settings'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, default='Invoice OCR Settings')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    auto_extract_on_upload = fields.Boolean(default=True)
    auto_match_vendor = fields.Boolean(default=True)
    auto_match_product = fields.Boolean(default=True)
    duplicate_check = fields.Boolean(default=True)
    min_confidence_approve = fields.Float(default=70.0, string='Min Confidence to Auto-Highlight')
    enable_gst_india = fields.Boolean(default=True, string='India GST Parsing')
    enable_llm_enhance = fields.Boolean(
        default=False,
        help='Use external LLM when companion module is installed.',
    )
    credit_balance = fields.Integer(default=100, string='OCR Credits Remaining')
    purchase_journal_id = fields.Many2one('account.journal', domain="[('type', '=', 'purchase')]")
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one invoice OCR settings record per company.',
    )
