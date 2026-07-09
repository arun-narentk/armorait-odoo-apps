# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHospitalInsurancePolicy(models.Model):
    _name = 'rn.hospital.insurance.policy'
    _description = 'Patient Insurance Policy'
    _order = 'valid_to desc'

    patient_id = fields.Many2one('rn.hospital.patient', required=True, ondelete='cascade', index=True)
    insurer_name = fields.Char(required=True)
    policy_number = fields.Char(required=True, index=True)
    tpa_name = fields.Char(string='TPA')
    valid_from = fields.Date()
    valid_to = fields.Date()
    coverage_amount = fields.Float()
    active = fields.Boolean(default=True)
