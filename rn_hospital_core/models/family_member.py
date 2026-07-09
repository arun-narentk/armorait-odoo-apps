# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHospitalFamilyMember(models.Model):
    _name = 'rn.hospital.family.member'
    _description = 'Patient Family Member'

    patient_id = fields.Many2one('rn.hospital.patient', required=True, ondelete='cascade')
    name = fields.Char(required=True)
    relation = fields.Selection(
        [
            ('spouse', 'Spouse'),
            ('parent', 'Parent'),
            ('child', 'Child'),
            ('sibling', 'Sibling'),
            ('other', 'Other'),
        ],
        default='other',
    )
    mobile = fields.Char()
    linked_patient_id = fields.Many2one('rn.hospital.patient', string='Linked Patient Record')
