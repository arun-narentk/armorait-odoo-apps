# -*- coding: utf-8 -*-
"""Rooms, chairs, vehicles, and other bookable resources."""

from odoo import fields, models


class RnBookingResource(models.Model):
    """Shared resource that can be reserved with an appointment."""

    _name = 'rn.booking.resource'
    _description = 'Booking Resource'
    _order = 'name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    active = fields.Boolean(default=True)
    resource_type = fields.Selection(
        selection=[
            ('room', 'Room'),
            ('chair', 'Chair'),
            ('equipment', 'Equipment'),
            ('vehicle', 'Vehicle'),
            ('other', 'Other'),
        ],
        default='room',
        required=True,
    )
    location_id = fields.Many2one('rn.booking.location', required=True, index=True)
    capacity = fields.Integer(default=1)
    color = fields.Integer()
    company_id = fields.Many2one(
        'res.company',
        related='location_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Text()
