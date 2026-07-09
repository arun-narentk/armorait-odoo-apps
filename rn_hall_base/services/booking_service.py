# -*- coding: utf-8 -*-
"""Booking conflict detection and calendar helpers."""

import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)

BLOCKING_STATES = ('tentative', 'waitlist', 'confirmed')


class RnHallBookingService(models.AbstractModel):
    """Booking overlap checks and upcoming event lists."""

    _name = 'rn.hall.booking.service'
    _description = 'Hall Booking Service'

    def find_conflicts(self, hall_id, date_start, date_end, exclude_id=None, states=None):
        states = states or BLOCKING_STATES
        domain = [
            ('hall_id', '=', hall_id),
            ('state', 'in', states),
            ('date_start', '<', date_end),
            ('date_end', '>', date_start),
        ]
        if exclude_id:
            domain.append(('id', '!=', exclude_id))
        return self.env['rn.hall.booking'].search(domain)

    def get_upcoming_bookings(self, company_id=None, days=30, limit=10):
        company_id = company_id or self.env.company.id
        today = fields.Datetime.now()
        end = today + timedelta(days=days)
        bookings = self.env['rn.hall.booking'].search([
            ('company_id', '=', company_id),
            ('date_start', '>=', today),
            ('date_start', '<=', end),
            ('state', 'in', BLOCKING_STATES),
        ], order='date_start', limit=limit)
        return [{
            'id': b.id,
            'name': b.name,
            'reference': b.reference,
            'hall': b.hall_id.name,
            'venue': b.venue_id.name,
            'function_type': b.function_type,
            'date_start': fields.Datetime.to_string(b.date_start),
            'state': b.state,
            'customer': b.partner_id.name or '',
        } for b in bookings]

    def get_occupancy_rate(self, company_id=None, days=30):
        """Simple occupancy: confirmed bookings vs hall-days in window."""
        company_id = company_id or self.env.company.id
        halls = self.env['rn.hall.hall'].search_count([('company_id', '=', company_id), ('active', '=', True)])
        if not halls:
            return 0.0
        today = fields.Date.context_today(self)
        end = today + timedelta(days=days)
        confirmed = self.env['rn.hall.booking'].search_count([
            ('company_id', '=', company_id),
            ('state', '=', 'confirmed'),
            ('date_start', '>=', fields.Datetime.to_datetime(today)),
            ('date_start', '<=', fields.Datetime.to_datetime(end)),
        ])
        capacity = halls * days
        return round((confirmed / capacity) * 100, 1) if capacity else 0.0
