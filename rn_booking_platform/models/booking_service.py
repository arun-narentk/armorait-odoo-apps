# -*- coding: utf-8 -*-
"""Bookable services."""

from odoo import fields, models


class RnBookingService(models.Model):
    """A service customers can book."""

    _name = 'rn.booking.service'
    _description = 'Booking Service'
    _order = 'sequence, name'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, tracking=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    industry_id = fields.Many2one('rn.booking.industry')
    location_ids = fields.Many2many('rn.booking.location', string='Locations')
    staff_ids = fields.Many2many(
        'rn.booking.staff',
        'rn_booking_service_staff_rel',
        'service_id',
        'staff_id',
        string='Staff',
    )
    duration_minutes = fields.Integer(default=30, required=True)
    buffer_before = fields.Integer(string='Buffer Before (min)', default=0)
    buffer_after = fields.Integer(string='Buffer After (min)', default=0)
    list_price = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    product_id = fields.Many2one('product.product', string='Invoicing Product')
    color = fields.Integer()
    requires_resource = fields.Boolean()
    resource_ids = fields.Many2many('rn.booking.resource', string='Resources')
    online_meeting = fields.Boolean(string='Online Meeting')
    meeting_provider = fields.Selection(
        selection=[
            ('none', 'None'),
            ('google_meet', 'Google Meet'),
            ('zoom', 'Zoom'),
            ('teams', 'Microsoft Teams'),
        ],
        default='none',
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    description = fields.Html()
