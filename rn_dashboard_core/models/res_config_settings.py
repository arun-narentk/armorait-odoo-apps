# -*- coding: utf-8 -*-
"""Settings bridge for Dashboard Core."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rn_dashboard_default_refresh = fields.Integer(
        related='company_id.rn_dashboard_default_refresh',
        readonly=False,
    )
    rn_dashboard_cache_ttl = fields.Integer(
        related='company_id.rn_dashboard_cache_ttl',
        readonly=False,
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    rn_dashboard_default_refresh = fields.Integer(default=30)
    rn_dashboard_cache_ttl = fields.Integer(default=60)
