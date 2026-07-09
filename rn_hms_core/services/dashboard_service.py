# -*- coding: utf-8 -*-
"""OWL hospital dashboard KPIs."""

import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnHmsDashboardService(models.AbstractModel):
    """Build Hospital ERP dashboard payload."""

    _name = 'rn.hms.dashboard.service'
    _description = 'HMS Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        start = fields.Datetime.to_string(fields.Datetime.to_datetime(today))
        end = fields.Datetime.to_string(fields.Datetime.to_datetime(today) + timedelta(days=1))
        Appt = self.env['rn.hms.appointment']
        domain = [('company_id', '=', company_id)]
        today_appts = Appt.search_count(domain + [
            ('start_datetime', '>=', start),
            ('start_datetime', '<', end),
            ('state', 'not in', ('cancel',)),
        ])
        waiting = Appt.search_count(domain + [('state', 'in', ('waiting', 'confirmed'))])
        patients = self.env['rn.hms.patient'].search_count(domain)
        doctors = self.env['rn.hms.doctor'].search_count(domain + [('active', '=', True)])
        bed_stats = self.env['rn.hms.bed.service'].occupancy_stats(company_id)
        return {
            'cards': {
                'today_appointments': today_appts,
                'patients_waiting': waiting,
                'bed_occupancy': bed_stats['occupancy_pct'],
                'beds_available': bed_stats['available'],
                'beds_occupied': bed_stats['occupied'],
                'patients': patients,
                'doctors': doctors,
                'revenue': 0.0,
                'pending_lab_reports': 0,
                'admissions': 0,
                'discharges': 0,
            },
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
