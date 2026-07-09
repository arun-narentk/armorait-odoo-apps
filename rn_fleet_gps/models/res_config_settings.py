# -*- coding: utf-8 -*-
"""Settings bridge."""

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    rn_fleet_overspeed_limit = fields.Float(default=80.0)
    rn_fleet_offline_minutes = fields.Integer(default=10)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rn_fleet_overspeed_limit = fields.Float(
        related='company_id.rn_fleet_overspeed_limit',
        readonly=False,
    )
    rn_fleet_offline_minutes = fields.Integer(
        related='company_id.rn_fleet_offline_minutes',
        readonly=False,
    )
