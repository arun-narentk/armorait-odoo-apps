# -*- coding: utf-8 -*-
"""Settings bridge."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    realestate_default_developer_id = fields.Many2one(
        related='company_id.realestate_default_developer_id',
        readonly=False,
    )
    realestate_developer_label = fields.Char(
        related='company_id.realestate_developer_label',
        readonly=False,
    )
    realestate_enable_portal = fields.Boolean(
        related='company_id.realestate_enable_portal',
        readonly=False,
    )
    realestate_enable_commission = fields.Boolean(
        related='company_id.realestate_enable_commission',
        readonly=False,
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    realestate_default_developer_id = fields.Many2one('rn.realestate.developer', string='Default Developer')
    realestate_developer_label = fields.Char(default='Builder')
    realestate_enable_portal = fields.Boolean(default=True)
    realestate_enable_commission = fields.Boolean(default=True)
