# -*- coding: utf-8 -*-

from odoo import models


class RnHospitalPatientService(models.AbstractModel):
    _name = 'rn.hospital.patient.service'
    _description = 'Patient Service'

    def get_patient_summary(self, patient_id):
        patient = self.env['rn.hospital.patient'].browse(patient_id)
        if not patient.exists():
            return {}
        return {
            'id': patient.id,
            'name': patient.name,
            'uhid': patient.uhid,
            'age': patient.age,
            'blood_group': patient.blood_group or '',
            'allergies': patient.allergy_ids.mapped('name'),
            'conditions': patient.condition_ids.filtered(lambda c: c.status == 'active').mapped('name'),
            'last_visit': patient.encounter_ids[:1].encounter_datetime if patient.encounter_ids else False,
        }
