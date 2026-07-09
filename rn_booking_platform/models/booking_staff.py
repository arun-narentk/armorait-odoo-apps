# -*- coding: utf-8 -*-
"""Staff members who deliver appointments."""

from odoo import fields, models


class RnBookingStaff(models.Model):
    """Bookable staff / provider profile."""

    _name = 'rn.booking.staff'
    _description = 'Booking Staff'
    _order = 'name'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    user_id = fields.Many2one('res.users', string='Linked User')
    partner_id = fields.Many2one('res.partner', string='Contact')
    industry_id = fields.Many2one('rn.booking.industry')
    location_ids = fields.Many2many(
        'rn.booking.location',
        'rn_booking_location_staff_rel',
        'staff_id',
        'location_id',
        string='Locations',
    )
    service_ids = fields.Many2many(
        'rn.booking.service',
        'rn_booking_service_staff_rel',
        'staff_id',
        'service_id',
        string='Services',
    )
    color = fields.Integer()
    commission_pct = fields.Float(string='Commission %', digits=(16, 2))
    timezone = fields.Char(default='UTC')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    working_hour_ids = fields.One2many(
        'rn.booking.working.hour',
        'staff_id',
        string='Working Hours',
    )
    note = fields.Text()
