# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHospitalPatientCondition(models.Model):
    _name = 'rn.hospital.patient.condition'
    _description = 'Chronic Condition'
    _order = 'name'

    patient_id = fields.Many2one('rn.hospital.patient', required=True, ondelete='cascade', index=True)
    name = fields.Char(required=True)
    diagnosed_date = fields.Date()
    status = fields.Selection(
        [('active', 'Active'), ('controlled', 'Controlled'), ('resolved', 'Resolved')],
        default='active',
    )
    note = fields.Text()
