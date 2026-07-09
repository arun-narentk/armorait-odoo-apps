# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHospitalConsentRecord(models.Model):
    _name = 'rn.hospital.consent.record'
    _description = 'Patient Consent Record'
    _order = 'consent_date desc'

    patient_id = fields.Many2one('rn.hospital.patient', required=True, ondelete='cascade', index=True)
    consent_type = fields.Selection(
        [
            ('treatment', 'Treatment'),
            ('surgery', 'Surgery'),
            ('data_privacy', 'Data Privacy'),
            ('photography', 'Photography'),
            ('other', 'Other'),
        ],
        required=True,
    )
    consent_date = fields.Datetime(default=fields.Datetime.now, required=True)
    signed_by = fields.Char()
    attachment_ids = fields.Many2many('ir.attachment', string='Signed Document')
    note = fields.Text()
