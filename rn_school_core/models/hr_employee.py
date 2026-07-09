# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_teacher = fields.Boolean(string='Is Teacher')
    subject_specialization = fields.Char(string='Subject')
    employee_code = fields.Char(string='Staff Code')
