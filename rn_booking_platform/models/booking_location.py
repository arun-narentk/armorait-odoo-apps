# -*- coding: utf-8 -*-
"""Branches / locations for multi-branch booking."""

from odoo import fields, models


class RnBookingLocation(models.Model):
    """Physical or virtual booking location."""

    _name = 'rn.booking.location'
    _description = 'Booking Location'
    _order = 'name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    active = fields.Boolean(default=True)
    industry_id = fields.Many2one('rn.booking.industry')
    partner_id = fields.Many2one('res.partner', string='Address Contact')
    timezone = fields.Char(default='UTC')
    phone = fields.Char()
    email = fields.Char()
    is_online = fields.Boolean(string='Online / Virtual')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    staff_ids = fields.Many2many(
        'rn.booking.staff',
        'rn_booking_location_staff_rel',
        'location_id',
        'staff_id',
        string='Staff',
    )
    resource_ids = fields.One2many('rn.booking.resource', 'location_id', string='Resources')
    note = fields.Text()
