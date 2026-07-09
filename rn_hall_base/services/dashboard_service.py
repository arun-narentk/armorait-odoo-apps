# -*- coding: utf-8 -*-
"""Hall operations dashboard."""

import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnHallDashboardService(models.AbstractModel):
    """Build Marriage Hall Management dashboard payload."""

    _name = 'rn.hall.dashboard.service'
    _description = 'Hall Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        end = today + timedelta(days=30)
        Booking = self.env['rn.hall.booking']
        domain = [('company_id', '=', company_id)]
        upcoming = Booking.search_count(domain + [
            ('date_start', '>=', fields.Datetime.to_datetime(today)),
            ('date_start', '<=', fields.Datetime.to_datetime(end)),
            ('state', 'in', ('tentative', 'waitlist', 'confirmed')),
        ])
        return {
            'cards': {
                'venues': self.env['rn.hall.venue'].search_count(domain),
                'halls': self.env['rn.hall.hall'].search_count(domain + [('active', '=', True)]),
                'upcoming_bookings': upcoming,
                'confirmed_bookings': Booking.search_count(domain + [('state', '=', 'confirmed')]),
                'tentative_bookings': Booking.search_count(domain + [('state', '=', 'tentative')]),
                'waitlist_bookings': Booking.search_count(domain + [('state', '=', 'waitlist')]),
                'occupancy_rate': self.env['rn.hall.booking.service'].get_occupancy_rate(company_id),
            },
            'bookings': self.env['rn.hall.booking.service'].get_upcoming_bookings(
                company_id=company_id,
                days=60,
                limit=10,
            ),
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
