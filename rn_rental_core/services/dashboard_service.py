# -*- coding: utf-8 -*-
"""OWL rental dashboard KPIs."""

import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnRentalDashboardService(models.AbstractModel):
    """Build ARMORA Rental dashboard payload."""

    _name = 'rn.rental.dashboard.service'
    _description = 'Rental Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        start = fields.Datetime.to_string(fields.Datetime.to_datetime(today))
        end = fields.Datetime.to_string(fields.Datetime.to_datetime(today) + timedelta(days=1))
        domain = [('company_id', '=', company_id)]
        Booking = self.env['rn.rental.booking']
        Asset = self.env['rn.rental.asset']
        today_rentals = Booking.search_count(domain + [
            ('date_start', '>=', start),
            ('date_start', '<', end),
            ('state', 'in', ('reserved', 'confirmed', 'picked_up')),
        ])
        returns_today = Booking.search_count(domain + [
            ('date_end', '>=', start),
            ('date_end', '<', end),
            ('state', 'in', ('confirmed', 'picked_up', 'returned')),
        ])
        assets = Asset.search(domain)
        in_use = assets.filtered(lambda a: a.state in ('booked', 'picked_up', 'in_use', 'reserved'))
        utilization = (len(in_use) / len(assets) * 100.0) if assets else 0.0
        revenue = sum(Booking.search(domain + [
            ('state', 'in', ('confirmed', 'picked_up', 'returned', 'done')),
        ]).mapped('amount_total'))
        return {
            'cards': {
                'today_rentals': today_rentals,
                'returns_today': returns_today,
                'revenue': revenue,
                'utilization': utilization,
                'late_returns': 0,
                'damaged_assets': Asset.search_count(domain + [('state', '=', 'damaged')]),
                'available_assets': Asset.search_count(domain + [('state', '=', 'available')]),
                'outstanding_deposits': 0.0,
            },
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
