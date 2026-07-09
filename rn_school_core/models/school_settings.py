# -*- coding: utf-8 -*-

from odoo import fields, models


class RnSchoolSettings(models.Model):
    _name = 'rn.school.settings'
    _description = 'School Settings'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', index=True)
    current_academic_year_id = fields.Many2one('rn.school.academic.year')
    ai_report_comments = fields.Boolean(default=True, string='AI Report Card Comments')
    ai_risk_detection = fields.Boolean(default=True, string='AI Student Risk Detection')
    parent_portal_enabled = fields.Boolean(default=True)
    attendance_notify_parents = fields.Boolean(default=True)
    fee_reminder_days = fields.Integer(default=3)
    admission_prefix = fields.Char(default='ADM')
    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Only one school settings record per company.'),
    ]
