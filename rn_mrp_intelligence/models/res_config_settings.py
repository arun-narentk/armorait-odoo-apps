# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mrp_intel_enable_ai = fields.Boolean(
        related='company_id.mrp_intel_enable_ai',
        readonly=False,
    )
    mrp_intel_oee_target = fields.Float(
        related='company_id.mrp_intel_oee_target',
        readonly=False,
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    mrp_intel_enable_ai = fields.Boolean(default=True)
    mrp_intel_oee_target = fields.Float(default=75.0)
