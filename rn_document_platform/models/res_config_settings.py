# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    doc_platform_enable_ai = fields.Boolean(
        related='company_id.doc_platform_enable_ai',
        readonly=False,
    )
    doc_platform_expiry_days = fields.Integer(
        related='company_id.doc_platform_expiry_days',
        readonly=False,
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    doc_platform_enable_ai = fields.Boolean(default=True)
    doc_platform_expiry_days = fields.Integer(default=14)
