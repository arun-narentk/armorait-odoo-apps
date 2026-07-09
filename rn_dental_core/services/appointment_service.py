# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields, models


class RnDentalAppointmentService(models.AbstractModel):
    _name = 'rn.dental.appointment.service'
    _description = 'Appointment Service'

    def schedule_appointment(self, patient_id, dentist_id, start_datetime, procedure_id=None, chair_id=None):
        procedure = self.env['rn.dental.procedure'].browse(procedure_id) if procedure_id else False
        duration = procedure.default_duration_minutes if procedure else 30
        end = start_datetime + timedelta(minutes=duration)
        appt = self.env['rn.dental.appointment'].create({
            'patient_id': patient_id,
            'dentist_id': dentist_id,
            'chair_id': chair_id,
            'procedure_id': procedure_id,
            'start_datetime': start_datetime,
            'end_datetime': end,
            'duration_minutes': duration,
            'state': 'scheduled',
        })
        return appt.id

    def check_in(self, appointment_id):
        self.env['rn.dental.appointment'].browse(appointment_id).action_check_in()
        return True

    def complete(self, appointment_id):
        self.env['rn.dental.appointment'].browse(appointment_id).action_complete()
        return True

    def today_for_dentist(self, dentist_id, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        start = fields.Datetime.to_datetime(today)
        end = start + timedelta(days=1)
        return self.env['rn.dental.appointment'].search([
            ('company_id', '=', company_id),
            ('dentist_id', '=', dentist_id),
            ('start_datetime', '>=', start),
            ('start_datetime', '<', end),
            ('state', 'not in', ('cancelled', 'no_show')),
        ])
