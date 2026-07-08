# -*- coding: utf-8 -*-
"""Employee code and onboarding helpers."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnHrmsEmployeeService(models.AbstractModel):
    """Assign employee codes and manage onboarding flags."""

    _name = 'rn.hrms.employee.service'
    _description = 'HRMS Employee Service'

    def assign_employee_code(self, employees):
        """Generate rn_hrms_employee_code when missing."""
        settings = self.env['rn.hrms.settings'].search(
            [('company_id', '=', self.env.company.id)], limit=1
        )
        prefix = settings.employee_code_prefix if settings else (
            self.env['ir.config_parameter'].sudo().get_param(
                'rn_hrms_core.employee_code_prefix', 'EMP'
            )
        )
        for employee in employees:
            if employee.rn_hrms_employee_code:
                continue
            seq = self.env['ir.sequence'].next_by_code('rn.hrms.employee') or employee.id
            employee.rn_hrms_employee_code = '%s%s' % (prefix, seq)
        _logger.info('Assigned employee codes for %s employees', len(employees))
        return True

    def mark_onboarded(self, employees):
        employees.write({
            'rn_hrms_onboarded': True,
            'rn_hrms_joining_date': fields.Date.context_today(self),
        })
        return True
