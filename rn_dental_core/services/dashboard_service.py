# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields, models


class RnDentalDashboardService(models.AbstractModel):
    _name = 'rn.dental.dashboard.service'
    _description = 'Dental Dashboard Service'

    def get_clinic_dashboard(self, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        start = fields.Datetime.to_datetime(today)
        end = start + timedelta(days=1)
        Appointment = self.env['rn.dental.appointment']
        appts_today = Appointment.search([
            ('company_id', '=', company_id),
            ('start_datetime', '>=', start),
            ('start_datetime', '<', end),
        ])
        chairs = self.env['rn.dental.chair'].search_count([
            ('company_id', '=', company_id),
            ('active', '=', True),
        ])
        in_chair = len(appts_today.filtered(lambda a: a.state in ('checked_in', 'in_chair')))
        new_patients = self.env['rn.dental.patient'].search_count([
            ('company_id', '=', company_id),
            ('create_date', '>=', fields.Datetime.to_datetime(today.replace(day=1))),
        ])
        pending_recalls = self.env['rn.dental.recall'].search_count([
            ('company_id', '=', company_id),
            ('state', '=', 'pending'),
            ('due_date', '<=', today),
        ])
        return {
            'appointments_today': len(appts_today),
            'in_chair': in_chair,
            'chairs': chairs,
            'chair_utilization': round((in_chair / chairs) * 100, 1) if chairs else 0.0,
            'new_patients_month': new_patients,
            'pending_recalls': pending_recalls,
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }

    def get_dentist_dashboard(self, dentist_id=None, company_id=None):
        company_id = company_id or self.env.company.id
        dentist_id = dentist_id or self.env.user.employee_id.id
        appts = self.env['rn.dental.appointment.service'].today_for_dentist(dentist_id, company_id)
        pending_plans = self.env['rn.dental.treatment.plan'].search_count([
            ('company_id', '=', company_id),
            ('dentist_id', '=', dentist_id),
            ('state', 'in', ('approved', 'in_progress')),
        ])
        lab_pending = self.env['rn.dental.lab.request'].search_count([
            ('company_id', '=', company_id),
            ('dentist_id', '=', dentist_id),
            ('state', 'in', ('sent', 'in_progress')),
        ])
        return {
            'appointments_today': len(appts),
            'pending_treatments': pending_plans,
            'lab_pending': lab_pending,
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
