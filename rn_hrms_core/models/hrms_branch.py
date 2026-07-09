# -*- coding: utf-8 -*-
"""Company branches / work locations for HRMS."""

from odoo import fields, models


class RnHrmsBranch(models.Model):
    """Branch used across attendance, payroll, and org structure."""

    _name = 'rn.hrms.branch'
    _description = 'HRMS Branch'
    _order = 'name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one('res.partner', string='Address')
    manager_id = fields.Many2one('hr.employee', string='Branch Manager')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    employee_ids = fields.One2many('hr.employee', 'rn_hrms_branch_id', string='Employees')
    note = fields.Text()
