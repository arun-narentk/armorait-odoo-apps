# -*- coding: utf-8 -*-
"""Hospital patient master record."""

from odoo import api, fields, models


class RnHospitalPatient(models.Model):
    """Patient with UHID and clinical profile."""

    _name = 'rn.hospital.patient'
    _description = 'Hospital Patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    uhid = fields.Char(string='UHID', readonly=True, copy=False, index=True)
    partner_id = fields.Many2one('res.partner', string='Contact')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    date_of_birth = fields.Date()
    age = fields.Integer(compute='_compute_age')
    blood_group = fields.Selection(
        [
            ('a_pos', 'A+'), ('a_neg', 'A-'),
            ('b_pos', 'B+'), ('b_neg', 'B-'),
            ('ab_pos', 'AB+'), ('ab_neg', 'AB-'),
            ('o_pos', 'O+'), ('o_neg', 'O-'),
        ],
    )
    mobile = fields.Char()
    email = fields.Char()
    address = fields.Text()
    emergency_contact = fields.Char()
    emergency_phone = fields.Char()
    allergy_ids = fields.One2many('rn.hospital.patient.allergy', 'patient_id')
    condition_ids = fields.One2many('rn.hospital.patient.condition', 'patient_id')
    family_ids = fields.One2many('rn.hospital.family.member', 'patient_id')
    insurance_ids = fields.One2many('rn.hospital.insurance.policy', 'patient_id')
    consent_ids = fields.One2many('rn.hospital.consent.record', 'patient_id')
    appointment_ids = fields.One2many('rn.hospital.appointment', 'patient_id')
    encounter_ids = fields.One2many('rn.hospital.emr.encounter', 'patient_id')
    admission_ids = fields.One2many('rn.hospital.admission', 'patient_id')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    _sql_constraints = [
        ('uhid_company_uniq', 'unique(uhid, company_id)', 'UHID must be unique per company.'),
    ]

    @api.depends('date_of_birth')
    def _compute_age(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year - (
                    (today.month, today.day) < (rec.date_of_birth.month, rec.date_of_birth.day)
                )
            else:
                rec.age = 0

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if not vals.get('uhid'):
                vals['uhid'] = seq.next_by_code('rn.hospital.patient.uhid') or 'UHID'
        return super().create(vals_list)
