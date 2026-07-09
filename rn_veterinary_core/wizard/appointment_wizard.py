# -*- coding: utf-8 -*-

from odoo import fields, models


class RnVetAppointmentWizard(models.TransientModel):
    _name = 'rn.vet.appointment.wizard'
    _description = 'Quick Vet Appointment'

    pet_id = fields.Many2one('rn.vet.pet', required=True)
    veterinarian_id = fields.Many2one('hr.employee', string='Veterinarian', required=True)
    appointment_type = fields.Selection(
        [
            ('consultation', 'Consultation'),
            ('vaccination', 'Vaccination'),
            ('surgery', 'Surgery'),
            ('grooming', 'Grooming'),
            ('boarding', 'Boarding'),
            ('emergency', 'Emergency'),
        ],
        default='consultation',
        required=True,
    )
    start_datetime = fields.Datetime(required=True, default=fields.Datetime.now)
    reason = fields.Text()

    def action_schedule(self):
        self.ensure_one()
        appt_id = self.env['rn.vet.appointment.service'].schedule(
            self.pet_id.id,
            self.veterinarian_id.id,
            self.start_datetime,
            appointment_type=self.appointment_type,
            reason=self.reason,
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.vet.appointment',
            'res_id': appt_id,
            'view_mode': 'form',
            'target': 'current',
        }
