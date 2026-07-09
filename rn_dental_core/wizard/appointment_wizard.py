# -*- coding: utf-8 -*-

from odoo import fields, models


class RnDentalAppointmentWizard(models.TransientModel):
    _name = 'rn.dental.appointment.wizard'
    _description = 'Quick Appointment'

    patient_id = fields.Many2one('rn.dental.patient', required=True)
    dentist_id = fields.Many2one('hr.employee', string='Dentist', required=True)
    chair_id = fields.Many2one('rn.dental.chair')
    procedure_id = fields.Many2one('rn.dental.procedure')
    start_datetime = fields.Datetime(required=True, default=fields.Datetime.now)

    def action_schedule(self):
        self.ensure_one()
        appt_id = self.env['rn.dental.appointment.service'].schedule_appointment(
            self.patient_id.id,
            self.dentist_id.id,
            self.start_datetime,
            procedure_id=self.procedure_id.id if self.procedure_id else None,
            chair_id=self.chair_id.id if self.chair_id else None,
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.dental.appointment',
            'res_id': appt_id,
            'view_mode': 'form',
            'target': 'current',
        }
