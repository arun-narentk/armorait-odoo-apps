# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHospitalPatientAllergy(models.Model):
    _name = 'rn.hospital.patient.allergy'
    _description = 'Patient Allergy'
    _order = 'severity desc, name'

    patient_id = fields.Many2one('rn.hospital.patient', required=True, ondelete='cascade', index=True)
    name = fields.Char(required=True)
    severity = fields.Selection(
        [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
        default='medium',
    )
    note = fields.Text()
