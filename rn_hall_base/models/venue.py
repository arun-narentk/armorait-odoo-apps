# -*- coding: utf-8 -*-
"""Venue / property master."""

from odoo import api, fields, models

VENUE_TYPES = [
    ('marriage_hall', 'Marriage Hall'),
    ('convention_center', 'Convention Center'),
    ('community_hall', 'Community Hall'),
    ('temple_hall', 'Temple Marriage Hall'),
    ('banquet_hall', 'Luxury Banquet Hall'),
    ('hotel_banquet', 'Hotel Banquet Hall'),
    ('clubhouse', 'Clubhouse'),
    ('exhibition_hall', 'Exhibition Hall'),
    ('other', 'Other Venue'),
]


class RnHallVenue(models.Model):
    """Marriage hall center or multi-hall event property."""

    _name = 'rn.hall.venue'
    _description = 'Hall Venue'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(copy=False, index=True, default='New', tracking=True)
    active = fields.Boolean(default=True)
    venue_type = fields.Selection(
        selection=VENUE_TYPES,
        default='marriage_hall',
        required=True,
        tracking=True,
    )
    trust_name = fields.Char(string='Trust / Company Name', tracking=True)
    registration_no = fields.Char(string='Registration Number')
    gstin = fields.Char(string='GSTIN')
    partner_id = fields.Many2one('res.partner', string='Official Contact')
    phone = fields.Char()
    email = fields.Char()
    website = fields.Char()
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state')
    zip = fields.Char()
    country_id = fields.Many2one('res.country')
    timezone = fields.Selection(
        selection=lambda self: self.env['res.partner']._fields['tz'].selection,
        default=lambda self: self.env.user.tz or 'Asia/Kolkata',
    )
    established_date = fields.Date()
    hall_ids = fields.One2many('rn.hall.hall', 'venue_id', string='Halls')
    hall_count = fields.Integer(compute='_compute_counts')
    booking_ids = fields.One2many('rn.hall.booking', 'venue_id', string='Bookings')
    booking_count = fields.Integer(compute='_compute_counts')
    upcoming_booking_count = fields.Integer(compute='_compute_upcoming_bookings')
    total_capacity = fields.Integer(compute='_compute_total_capacity', string='Total Seating')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Html()

    @api.depends('hall_ids', 'booking_ids')
    def _compute_counts(self):
        for venue in self:
            venue.hall_count = len(venue.hall_ids)
            venue.booking_count = len(venue.booking_ids)

    @api.depends('hall_ids', 'hall_ids.capacity_seated')
    def _compute_total_capacity(self):
        for venue in self:
            venue.total_capacity = sum(venue.hall_ids.mapped('capacity_seated'))

    @api.depends('booking_ids', 'booking_ids.date_start', 'booking_ids.state')
    def _compute_upcoming_bookings(self):
        today = fields.Date.context_today(self)
        Booking = self.env['rn.hall.booking']
        for venue in self:
            venue.upcoming_booking_count = Booking.search_count([
                ('venue_id', '=', venue.id),
                ('date_start', '>=', today),
                ('state', 'in', ('tentative', 'waitlist', 'confirmed')),
            ])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.hall.venue') or 'New'
        return super().create(vals_list)

    def action_open_halls(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Halls',
            'res_model': 'rn.hall.hall',
            'view_mode': 'list,form,calendar',
            'domain': [('venue_id', '=', self.id)],
            'context': {'default_venue_id': self.id},
        }

    def action_open_bookings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bookings',
            'res_model': 'rn.hall.booking',
            'view_mode': 'calendar,list,form',
            'domain': [('venue_id', '=', self.id)],
            'context': {'default_venue_id': self.id},
        }
