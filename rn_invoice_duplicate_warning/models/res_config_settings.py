# -*- coding: utf-8 -*-
"""Accounting settings for duplicate vendor invoice warnings."""

from odoo import fields, models

from .constants import PARAM_BLOCK, PARAM_CASE_INSENSITIVE, PARAM_ENABLE


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rn_enable_duplicate_invoice_warning = fields.Boolean(
        string='Enable Duplicate Invoice Number Warning',
        config_parameter=PARAM_ENABLE,
        default=True,
        help='Warn users when a vendor invoice with the same invoice number already '
             'exists for the same vendor and company.',
    )
    rn_block_duplicate_invoice = fields.Boolean(
        string='Block Duplicate Vendor Invoice',
        config_parameter=PARAM_BLOCK,
        default=False,
        help='When enabled, users cannot post a vendor bill if a duplicate invoice '
             'number is detected.',
    )
    rn_duplicate_invoice_case_insensitive = fields.Boolean(
        string='Case-Insensitive Invoice Numbers',
        config_parameter=PARAM_CASE_INSENSITIVE,
        default=True,
        help='Treat INV-1001 and inv-1001 as the same vendor invoice number.',
    )
