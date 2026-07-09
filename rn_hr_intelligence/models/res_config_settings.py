# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hr_intel_enable_ai = fields.Boolean(
        related='company_id.hr_intel_enable_ai',
        readonly=False,
    )
    hr_intel_overtime_threshold = fields.Float(
        related='company_id.hr_intel_overtime_threshold',
        readonly=False,
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    hr_intel_enable_ai = fields.Boolean(default=True)
    hr_intel_overtime_threshold = fields.Float(default=48.0)
