# -*- coding: utf-8 -*-
"""Settings bridge."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    temple_default_temple_id = fields.Many2one(
        related='company_id.temple_default_temple_id',
        readonly=False,
    )
    temple_institution_label = fields.Char(
        related='company_id.temple_institution_label',
        readonly=False,
    )
    temple_enable_online_booking = fields.Boolean(
        related='company_id.temple_enable_online_booking',
        readonly=False,
    )
    temple_enable_donation_portal = fields.Boolean(
        related='company_id.temple_enable_donation_portal',
        readonly=False,
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    temple_default_temple_id = fields.Many2one('rn.temple.temple', string='Default Temple')
    temple_institution_label = fields.Char(default='Temple')
    temple_enable_online_booking = fields.Boolean(default=True)
    temple_enable_donation_portal = fields.Boolean(default=True)
