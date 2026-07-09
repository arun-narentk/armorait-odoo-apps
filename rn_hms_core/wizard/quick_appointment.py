# -*- coding: utf-8 -*-
"""Quick appointment booking wizard."""

from datetime import timedelta

from odoo import fields, models


class RnHmsQuickAppointmentWizard(models.TransientModel):
    """Create an OPD appointment quickly."""

    _name = 'rn.hms.quick.appointment.wizard'
    _description = 'Quick Appointment Wizard'

    patient_id = fields.Many2one('rn.hms.patient', required=True)
    doctor_id = fields.Many2one('rn.hms.doctor', required=True)
    department_id = fields.Many2one('rn.hms.department')
    start_datetime = fields.Datetime(required=True, default=fields.Datetime.now)
    chief_complaint = fields.Text()
    appointment_type = fields.Selection(
        selection=[
            ('opd', 'OPD'),
            ('followup', 'Follow-up'),
            ('walkin', 'Walk-in'),
            ('online', 'Online'),
        ],
        default='opd',
        required=True,
    )

    def action_create(self):
        self.ensure_one()
        doctor = self.doctor_id
        stop = fields.Datetime.to_datetime(self.start_datetime) + timedelta(
            minutes=doctor.consultation_minutes or 15
        )
        appt = self.env['rn.hms.appointment'].create({
            'patient_id': self.patient_id.id,
            'doctor_id': doctor.id,
            'department_id': self.department_id.id if self.department_id else False,
            'start_datetime': self.start_datetime,
            'stop_datetime': fields.Datetime.to_string(stop),
            'chief_complaint': self.chief_complaint,
            'appointment_type': self.appointment_type,
            'fee': doctor.consulting_fee or 0.0,
            'company_id': doctor.company_id.id,
        })
        self.env['rn.hms.appointment.service'].confirm(appt)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.hms.appointment',
            'res_id': appt.id,
            'view_mode': 'form',
            'target': 'current',
        }
