# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields, models


class RnVetDashboardService(models.AbstractModel):
    _name = 'rn.vet.dashboard.service'
    _description = 'Veterinary Dashboard Service'

    def get_clinic_dashboard(self, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        start = fields.Datetime.to_datetime(today)
        end = start + timedelta(days=1)
        appts = self.env['rn.vet.appointment'].search_count([
            ('company_id', '=', company_id),
            ('start_datetime', '>=', start),
            ('start_datetime', '<', end),
        ])
        due_vaccines = self.env['rn.vet.vaccination.service'].due_vaccinations(company_id, within_days=14)
        boarding = self.env['rn.vet.boarding.service'].occupancy(company_id)
        grooming_month = self.env['rn.vet.grooming'].search_count([
            ('company_id', '=', company_id),
            ('grooming_date', '>=', fields.Datetime.to_datetime(today.replace(day=1))),
            ('state', '=', 'done'),
        ])
        return {
            'appointments_today': appts,
            'vaccinations_due': len(due_vaccines),
            'boarding_occupancy': boarding['occupancy_pct'],
            'kennels_occupied': boarding['occupied'],
            'grooming_month': grooming_month,
            'pet_count': self.env['rn.vet.pet'].search_count([
                ('company_id', '=', company_id),
                ('active', '=', True),
            ]),
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }

    def get_vet_dashboard(self, veterinarian_id=None, company_id=None):
        company_id = company_id or self.env.company.id
        veterinarian_id = veterinarian_id or self.env.user.employee_id.id
        appts = self.env['rn.vet.appointment.service'].today_for_vet(veterinarian_id, company_id)
        surgeries = self.env['rn.vet.surgery'].search_count([
            ('company_id', '=', company_id),
            ('surgeon_id', '=', veterinarian_id),
            ('state', 'in', ('scheduled', 'in_progress')),
        ])
        return {
            'appointments_today': len(appts),
            'surgeries_pending': surgeries,
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
