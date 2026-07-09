# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields, models


class RnVetAppointmentService(models.AbstractModel):
    _name = 'rn.vet.appointment.service'
    _description = 'Vet Appointment Service'

    def schedule(self, pet_id, veterinarian_id, start_datetime, appointment_type='consultation', reason=None):
        appt = self.env['rn.vet.appointment'].create({
            'pet_id': pet_id,
            'veterinarian_id': veterinarian_id,
            'start_datetime': start_datetime,
            'end_datetime': start_datetime + timedelta(minutes=30),
            'appointment_type': appointment_type,
            'reason': reason,
            'state': 'scheduled',
        })
        return appt.id

    def check_in(self, appointment_id):
        self.env['rn.vet.appointment'].browse(appointment_id).action_check_in()
        return True

    def today_for_vet(self, veterinarian_id, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        start = fields.Datetime.to_datetime(today)
        end = start + timedelta(days=1)
        return self.env['rn.vet.appointment'].search([
            ('company_id', '=', company_id),
            ('veterinarian_id', '=', veterinarian_id),
            ('start_datetime', '>=', start),
            ('start_datetime', '<', end),
            ('state', 'not in', ('cancelled', 'no_show')),
        ])
