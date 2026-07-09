# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.exceptions import UserError


class RnHospitalAppointmentService(models.AbstractModel):
    _name = 'rn.hospital.appointment.service'
    _description = 'Appointment Service'

    def book_appointment(self, patient_id, doctor_id, appointment_datetime, department_id=None, complaint=''):
        patient = self.env['rn.hospital.patient'].browse(patient_id)
        doctor = self.env['hr.employee'].browse(doctor_id)
        if not patient.exists() or not doctor.exists():
            raise UserError('Patient and doctor are required.')
        return self.env['rn.hospital.appointment'].create({
            'patient_id': patient.id,
            'doctor_id': doctor.id,
            'department_id': department_id,
            'appointment_datetime': appointment_datetime,
            'chief_complaint': complaint,
            'state': 'confirmed',
        }).id

    def assign_token(self, appointment_id):
        appt = self.env['rn.hospital.appointment'].browse(appointment_id)
        today = fields.Date.context_today(self)
        domain = [
            ('doctor_id', '=', appt.doctor_id.id),
            ('appointment_datetime', '>=', fields.Datetime.to_datetime(today)),
            ('token_number', '>', 0),
            ('company_id', '=', appt.company_id.id),
        ]
        last = self.env['rn.hospital.appointment'].search(domain, order='token_number desc', limit=1)
        return (last.token_number or 0) + 1

    def get_queue(self, doctor_id=None, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        domain = [
            ('company_id', '=', company_id),
            ('state', 'in', ('confirmed', 'waiting', 'in_consultation')),
            ('appointment_datetime', '>=', fields.Datetime.to_datetime(today)),
        ]
        if doctor_id:
            domain.append(('doctor_id', '=', doctor_id))
        appointments = self.env['rn.hospital.appointment'].search(domain, order='token_number, appointment_datetime')
        return [
            {
                'id': a.id,
                'name': a.name,
                'patient': a.patient_id.name,
                'uhid': a.patient_id.uhid,
                'token': a.token_number,
                'state': a.state,
                'doctor': a.doctor_id.name,
                'time': fields.Datetime.to_string(a.appointment_datetime),
            }
            for a in appointments
        ]
