# -*- coding: utf-8 -*-
"""Quick patient registration wizard."""

from odoo import fields, models


class RnHmsRegisterPatientWizard(models.TransientModel):
    """Collect patient basics and create record via service."""

    _name = 'rn.hms.register.patient.wizard'
    _description = 'Register Patient Wizard'

    name = fields.Char(required=True)
    phone = fields.Char()
    email = fields.Char()
    gender = fields.Selection(
        selection=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
    )
    birth_date = fields.Date()
    blood_group = fields.Selection(
        selection=[
            ('a+', 'A+'), ('a-', 'A-'),
            ('b+', 'B+'), ('b-', 'B-'),
            ('ab+', 'AB+'), ('ab-', 'AB-'),
            ('o+', 'O+'), ('o-', 'O-'),
        ],
    )
    emergency_contact = fields.Char()
    emergency_phone = fields.Char()

    def action_register(self):
        self.ensure_one()
        patient = self.env['rn.hms.patient.service'].register_patient({
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'gender': self.gender,
            'birth_date': self.birth_date,
            'blood_group': self.blood_group,
            'emergency_contact': self.emergency_contact,
            'emergency_phone': self.emergency_phone,
            'company_id': self.env.company.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.hms.patient',
            'res_id': patient.id,
            'view_mode': 'form',
            'target': 'current',
        }
