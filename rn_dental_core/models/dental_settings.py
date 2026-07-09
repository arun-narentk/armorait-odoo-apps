# -*- coding: utf-8 -*-

from odoo import fields, models


class RnDentalSettings(models.Model):
    _name = 'rn.dental.settings'
    _description = 'Dental Clinic Settings'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', index=True)
    clinic_name = fields.Char()
    default_appointment_minutes = fields.Integer(default=30)
    enable_online_booking = fields.Boolean(default=True)
    recall_checkup_months = fields.Integer(default=6)
    ai_clinical_notes = fields.Boolean(default=True)
    ai_recall = fields.Boolean(default=True)
    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Only one dental settings record per company.'),
    ]
