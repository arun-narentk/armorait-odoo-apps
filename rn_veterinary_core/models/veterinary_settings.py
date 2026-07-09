# -*- coding: utf-8 -*-

from odoo import fields, models


class RnVeterinarySettings(models.Model):
    _name = 'rn.veterinary.settings'
    _description = 'Veterinary Clinic Settings'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', index=True)
    clinic_name = fields.Char()
    default_appointment_minutes = fields.Integer(default=30)
    vaccination_reminder_days = fields.Integer(default=7)
    ai_clinical_notes = fields.Boolean(default=True)
    ai_vaccination = fields.Boolean(default=True)
    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Only one veterinary settings record per company.'),
    ]
