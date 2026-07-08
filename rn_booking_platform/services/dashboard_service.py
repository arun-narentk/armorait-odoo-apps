# -*- coding: utf-8 -*-
"""OWL dashboard KPI aggregation."""

import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnBookingDashboardService(models.AbstractModel):
    """Build booking dashboard payload."""

    _name = 'rn.booking.dashboard.service'
    _description = 'Booking Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        Appt = self.env['rn.booking.appointment']
        domain_company = [('company_id', '=', company_id)]
        start_today = fields.Datetime.to_string(
            fields.Datetime.to_datetime(today)
        )
        end_today = fields.Datetime.to_string(
            fields.Datetime.to_datetime(today) + timedelta(days=1)
        )
        today_count = Appt.search_count(domain_company + [
            ('start_datetime', '>=', start_today),
            ('start_datetime', '<', end_today),
            ('state', 'in', ('pending', 'confirmed', 'done')),
        ])
        upcoming = Appt.search_count(domain_company + [
            ('start_datetime', '>=', fields.Datetime.now()),
            ('state', 'in', ('pending', 'confirmed')),
        ])
        cancelled = Appt.search_count(domain_company + [('state', '=', 'cancel')])
        no_show = Appt.search_count(domain_company + [('state', '=', 'no_show')])
        paid = Appt.search(domain_company + [('payment_state', '=', 'paid')])
        revenue = sum(paid.mapped('amount_paid')) or sum(paid.mapped('amount_total'))
        recent = Appt.search(domain_company, order='start_datetime desc', limit=10)
        return {
            'cards': {
                'today_appointments': today_count,
                'upcoming_appointments': upcoming,
                'revenue': revenue,
                'cancellations': cancelled,
                'no_shows': no_show,
                'occupancy_rate': 0.0,
                'new_customers': 0,
                'repeat_customers': 0,
            },
            'recent': [
                {
                    'id': a.id,
                    'name': a.name,
                    'partner': a.partner_id.display_name,
                    'service': a.service_id.display_name,
                    'start': fields.Datetime.to_string(a.start_datetime),
                    'state': a.state,
                }
                for a in recent
            ],
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
