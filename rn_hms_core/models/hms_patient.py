# -*- coding: utf-8 -*-
"""Patient master for HMS."""

from odoo import api, fields, models


class RnHmsPatient(models.Model):
    """Registered patient with medical profile fields."""

    _name = 'rn.hms.patient'
    _description = 'HMS Patient'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    patient_code = fields.Char(copy=False, index=True, default='New', tracking=True)
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one('res.partner', string='Linked Contact', tracking=True)
    gender = fields.Selection(
        selection=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
    )
    birth_date = fields.Date()
    age = fields.Integer(compute='_compute_age', store=True)
    blood_group = fields.Selection(
        selection=[
            ('a+', 'A+'), ('a-', 'A-'),
            ('b+', 'B+'), ('b-', 'B-'),
            ('ab+', 'AB+'), ('ab-', 'AB-'),
            ('o+', 'O+'), ('o-', 'O-'),
        ],
    )
    phone = fields.Char()
    email = fields.Char()
    allergy_ids = fields.Text(string='Allergies')
    medical_history = fields.Html()
    family_history = fields.Html()
    emergency_contact = fields.Char()
    emergency_phone = fields.Char()
    insurance_provider = fields.Char()
    insurance_policy = fields.Char()
    image_1920 = fields.Image()
    appointment_ids = fields.One2many('rn.hms.appointment', 'patient_id', string='Appointments')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Text()

    @api.depends('birth_date')
    def _compute_age(self):
        today = fields.Date.context_today(self)
        for patient in self:
            if patient.birth_date:
                patient.age = today.year - patient.birth_date.year - (
                    (today.month, today.day) < (patient.birth_date.month, patient.birth_date.day)
                )
            else:
                patient.age = 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('patient_code', 'New') == 'New':
                vals['patient_code'] = self.env['ir.sequence'].next_by_code('rn.hms.patient') or 'New'
        return super().create(vals_list)
