# -*- coding: utf-8 -*-
"""Onboard selected employees."""

from odoo import fields, models


class RnHrmsEmployeeOnboardingWizard(models.TransientModel):
    """Run onboarding for one or more employees."""

    _name = 'rn.hrms.employee.onboarding.wizard'
    _description = 'Employee Onboarding Wizard'

    employee_ids = fields.Many2many('hr.employee', required=True)
    branch_id = fields.Many2one('rn.hrms.branch')
    designation_id = fields.Many2one('rn.hrms.designation')

    def action_onboard(self):
        self.ensure_one()
        vals = {}
        if self.branch_id:
            vals['rn_hrms_branch_id'] = self.branch_id.id
        if self.designation_id:
            vals['rn_hrms_designation_id'] = self.designation_id.id
        if vals:
            self.employee_ids.write(vals)
        for employee in self.employee_ids:
            self.env['rn.hrms.onboarding.service'].onboard_employee(employee)
        return {'type': 'ir.actions.act_window_close'}
