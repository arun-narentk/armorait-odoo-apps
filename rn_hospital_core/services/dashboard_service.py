# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHospitalDashboardService(models.AbstractModel):
    _name = 'rn.hospital.dashboard.service'
    _description = 'Hospital Dashboard Service'

    def get_hospital_dashboard(self, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        Appointment = self.env['rn.hospital.appointment']
        Admission = self.env['rn.hospital.admission']
        Billing = self.env['rn.hospital.billing.line']
        Bed = self.env['rn.hospital.bed']

        opd_today = Appointment.search_count([
            ('company_id', '=', company_id),
            ('appointment_datetime', '>=', fields.Datetime.to_datetime(today)),
        ])
        ip_active = Admission.search_count([
            ('company_id', '=', company_id),
            ('state', '=', 'admitted'),
        ])
        beds = Bed.search([('company_id', '=', company_id)])
        occupied = len(beds.filtered(lambda b: b.state == 'occupied'))
        revenue = sum(Billing.search([
            ('company_id', '=', company_id),
            ('charge_date', '>=', fields.Datetime.to_datetime(today)),
        ]).mapped('amount'))

        return {
            'opd_today': opd_today,
            'ip_admissions': ip_active,
            'bed_occupancy_pct': round((occupied / len(beds)) * 100, 1) if beds else 0.0,
            'revenue_today': revenue,
            'waiting_patients': Appointment.search_count([
                ('company_id', '=', company_id),
                ('state', '=', 'waiting'),
            ]),
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }

    def get_doctor_dashboard(self, doctor_id=None):
        doctor_id = doctor_id or self.env.user.employee_id.id
        if not doctor_id:
            return {'appointments': [], 'queue': []}
        today = fields.Date.context_today(self)
        appointments = self.env['rn.hospital.appointment'].search([
            ('doctor_id', '=', doctor_id),
            ('appointment_datetime', '>=', fields.Datetime.to_datetime(today)),
            ('state', 'not in', ('cancelled', 'no_show')),
        ], order='appointment_datetime')
        queue = self.env['rn.hospital.appointment.service'].get_queue(doctor_id=doctor_id)
        return {
            'doctor_name': self.env['hr.employee'].browse(doctor_id).name,
            'appointments_today': len(appointments),
            'in_consultation': len(appointments.filtered(lambda a: a.state == 'in_consultation')),
            'queue': queue,
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
