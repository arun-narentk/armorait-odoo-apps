# -*- coding: utf-8 -*-
"""Company IDP settings and usage credits."""

from odoo import fields, models


class RnDocumentIdpSettings(models.Model):
    _name = 'rn.document.idp.settings'
    _description = 'IDP Settings'
    _rec_name = 'name'

    name = fields.Char(default='IDP Settings', required=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    credit_balance = fields.Integer(default=500, string='Document Credits')
    auto_post_confidence = fields.Float(
        default=95.0,
        string='Auto-Post Confidence %',
        help='Documents above this score can be auto-posted when policy allows.',
    )
    enable_gst_india = fields.Boolean(default=True)
    enable_duplicate_check = fields.Boolean(default=True)
    enable_three_way_match = fields.Boolean(default=True)
    qty_tolerance_percent = fields.Float(default=5.0, string='Qty Tolerance %')
    price_tolerance_percent = fields.Float(default=2.0, string='Price Tolerance %')
    fraud_alert_threshold = fields.Float(default=60.0, string='Fraud Alert Score')
