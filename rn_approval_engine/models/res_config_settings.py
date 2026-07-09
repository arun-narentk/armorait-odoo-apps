# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    approval_enable_email = fields.Boolean(
        related='company_id.approval_enable_email',
        readonly=False,
    )
    approval_enable_ai_risk = fields.Boolean(
        related='company_id.approval_enable_ai_risk',
        readonly=False,
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    approval_enable_email = fields.Boolean(default=True)
    approval_enable_ai_risk = fields.Boolean(default=True)
