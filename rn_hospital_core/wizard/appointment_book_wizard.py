# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHospitalAppointmentBookWizard(models.TransientModel):
    _name = 'rn.hospital.appointment.book.wizard'
    _description = 'Book Appointment Wizard'

    patient_id = fields.Many2one('rn.hospital.patient', required=True)
    doctor_id = fields.Many2one('hr.employee', required=True, domain=[('is_doctor', '=', True)])
    department_id = fields.Many2one('rn.hospital.department')
    appointment_datetime = fields.Datetime(required=True, default=fields.Datetime.now)
    chief_complaint = fields.Text()

    def action_book(self):
        self.ensure_one()
        appt_id = self.env['rn.hospital.appointment.service'].book_appointment(
            self.patient_id.id,
            self.doctor_id.id,
            self.appointment_datetime,
            department_id=self.department_id.id,
            complaint=self.chief_complaint or '',
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.hospital.appointment',
            'res_id': appt_id,
            'view_mode': 'form',
            'target': 'current',
        }
