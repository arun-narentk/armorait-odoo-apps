# -*- coding: utf-8 -*-

from odoo import fields, models


class RnDentalPatient(models.Model):
    _name = 'rn.dental.patient'
    _description = 'Dental Patient'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(index=True)
    mobile = fields.Char(index=True)
    email = fields.Char()
    date_of_birth = fields.Date()
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    address = fields.Text()
    allergies = fields.Text()
    medical_history = fields.Text()
    dental_history = fields.Text()
    family_head_id = fields.Many2one('rn.dental.patient', string='Family Head')
    consent_signed = fields.Boolean(string='Consent on File')
    clinical_notes = fields.Html()
    partner_id = fields.Many2one('res.partner')
    appointment_ids = fields.One2many('rn.dental.appointment', 'patient_id')
    treatment_plan_ids = fields.One2many('rn.dental.treatment.plan', 'patient_id')
    tooth_record_ids = fields.One2many('rn.dental.tooth.record', 'patient_id')
    imaging_ids = fields.One2many('rn.dental.imaging', 'patient_id')
    recall_ids = fields.One2many('rn.dental.recall', 'patient_id')
    referral_source = fields.Char()
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
