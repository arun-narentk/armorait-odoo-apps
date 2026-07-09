# -*- coding: utf-8 -*-
"""Settings bridge."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hall_default_venue_id = fields.Many2one(
        related='company_id.hall_default_venue_id',
        readonly=False,
    )
    hall_venue_label = fields.Char(
        related='company_id.hall_venue_label',
        readonly=False,
    )
    hall_enable_online_booking = fields.Boolean(
        related='company_id.hall_enable_online_booking',
        readonly=False,
    )
    hall_enable_conflict_block = fields.Boolean(
        related='company_id.hall_enable_conflict_block',
        readonly=False,
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    hall_default_venue_id = fields.Many2one('rn.hall.venue', string='Default Venue')
    hall_venue_label = fields.Char(default='Marriage Hall')
    hall_enable_online_booking = fields.Boolean(default=True)
    hall_enable_conflict_block = fields.Boolean(default=True)
