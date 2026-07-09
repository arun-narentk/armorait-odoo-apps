# -*- coding: utf-8 -*-

from odoo import models
from odoo.exceptions import UserError


class RnHospitalEmrService(models.AbstractModel):
    _name = 'rn.hospital.emr.service'
    _description = 'EMR Service'

    def start_encounter_from_appointment(self, appointment_id):
        appt = self.env['rn.hospital.appointment'].browse(appointment_id)
        if not appt.exists():
            raise UserError('Appointment not found.')
        if appt.encounter_id:
            return appt.encounter_id.id
        encounter = self.env['rn.hospital.emr.encounter'].create({
            'patient_id': appt.patient_id.id,
            'doctor_id': appt.doctor_id.id,
            'appointment_id': appt.id,
            'department_id': appt.department_id.id,
            'chief_complaint': appt.chief_complaint,
            'state': 'in_progress',
        })
        appt.write({'encounter_id': encounter.id, 'state': 'in_consultation'})
        return encounter.id

    def add_prescription_line(self, encounter_id, medicine_name, dosage='', frequency='', duration_days=0):
        encounter = self.env['rn.hospital.emr.encounter'].browse(encounter_id)
        if not encounter.exists():
            raise UserError('Encounter not found.')
        warning = self.env['rn.hospital.insight.service'].check_prescription_allergy(
            encounter.patient_id.id, medicine_name
        )
        return self.env['rn.hospital.emr.prescription'].create({
            'encounter_id': encounter.id,
            'medicine_name': medicine_name,
            'dosage': dosage,
            'frequency': frequency,
            'duration_days': duration_days,
            'ai_warning': warning or '',
        }).id
