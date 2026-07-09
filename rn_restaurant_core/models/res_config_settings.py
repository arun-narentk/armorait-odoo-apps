# -*- coding: utf-8 -*-
"""Settings bridge for Restaurant Core."""

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    rn_restaurant_default_prep = fields.Integer(default=12)
    rn_restaurant_enable_tables = fields.Boolean(default=True)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rn_restaurant_default_prep = fields.Integer(
        related='company_id.rn_restaurant_default_prep',
        readonly=False,
    )
    rn_restaurant_enable_tables = fields.Boolean(
        related='company_id.rn_restaurant_enable_tables',
        readonly=False,
    )
