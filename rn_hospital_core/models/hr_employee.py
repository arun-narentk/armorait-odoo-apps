# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_doctor = fields.Boolean(string='Is Doctor')
    medical_registration = fields.Char(string='Medical Registration No.')
    specialization = fields.Char()
    department_id = fields.Many2one('rn.hospital.department', string='Hospital Department')
    consultation_fee = fields.Float()
