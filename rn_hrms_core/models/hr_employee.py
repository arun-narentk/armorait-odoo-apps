# -*- coding: utf-8 -*-
"""Employee extensions for ARMORA HRMS."""

from odoo import fields, models


class HrEmployee(models.Model):
    """Add HRMS fields used by companion modules."""

    _inherit = 'hr.employee'

    rn_hrms_branch_id = fields.Many2one('rn.hrms.branch', string='Branch', index=True)
    rn_hrms_designation_id = fields.Many2one('rn.hrms.designation', string='Designation')
    rn_hrms_employee_code = fields.Char(string='Employee Code', copy=False, index=True)
    rn_hrms_joining_date = fields.Date(string='Joining Date')
    rn_hrms_confirmation_date = fields.Date(string='Confirmation Date')
    rn_hrms_resignation_date = fields.Date(string='Resignation Date')
    rn_hrms_employment_type = fields.Selection(
        selection=[
            ('permanent', 'Permanent'),
            ('contract', 'Contract'),
            ('intern', 'Intern'),
            ('consultant', 'Consultant'),
        ],
        default='permanent',
        string='Employment Type',
    )
    rn_hrms_emergency_contact = fields.Char(string='Emergency Contact')
    rn_hrms_emergency_phone = fields.Char(string='Emergency Phone')
    rn_hrms_skill_ids = fields.Many2many(
        'rn.hrms.skill',
        'rn_hrms_employee_skill_rel',
        'employee_id',
        'skill_id',
        string='Skills',
    )
    rn_hrms_document_ids = fields.One2many(
        'rn.hrms.document',
        'employee_id',
        string='HR Documents',
    )
    rn_hrms_onboarded = fields.Boolean(string='Onboarded', default=False)
