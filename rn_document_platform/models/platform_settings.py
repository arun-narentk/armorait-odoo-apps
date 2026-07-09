# -*- coding: utf-8 -*-
"""Platform settings and SaaS credits."""

from odoo import fields, models


class RnDocPlatformSettings(models.Model):
    """Per-company digital document platform configuration."""

    _name = 'rn.doc.platform.settings'
    _description = 'Document Platform Settings'
    _inherit = ['mail.thread']

    name = fields.Char(default='Document Platform Settings', required=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    enable_ai_analysis = fields.Boolean(default=True)
    default_expiry_days = fields.Integer(default=14)
    signature_credit_balance = fields.Integer(default=100)
    enable_email_invite = fields.Boolean(default=True)
    enable_whatsapp_delivery = fields.Boolean(
        default=False,
        help='Requires rn_whatsapp_connector companion module.',
    )
    require_audit_hash = fields.Boolean(default=True, string='Store Document Hash')
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one document platform settings record per company.',
    )
