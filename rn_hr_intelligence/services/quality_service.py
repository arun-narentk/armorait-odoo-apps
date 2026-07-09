# -*- coding: utf-8 -*-
"""HR data quality validation."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnHrQualityService(models.AbstractModel):
    """Scan HR master data for analytics gaps."""

    _name = 'rn.hr.quality.service'
    _description = 'HR Quality Service'

    def run_quality_checks(self, company_id=None):
        company_id = company_id or self.env.company.id
        Check = self.env['rn.hr.data.quality.check']
        Check.search([('company_id', '=', company_id), ('resolved', '=', False)]).unlink()
        issues = []
        employees = self.env['hr.employee'].search([
            ('company_id', '=', company_id),
            ('active', '=', True),
        ])
        for emp in employees:
            if not emp.department_id:
                issues.append(self._create_check(
                    company_id, 'missing_department', emp,
                    f'{emp.name} has no department assigned.',
                ))
            contract = self.env['hr.contract'].search([
                ('employee_id', '=', emp.id),
                ('state', '=', 'open'),
            ], limit=1)
            if not contract:
                issues.append(self._create_check(
                    company_id, 'missing_contract', emp,
                    f'{emp.name} has no open contract.',
                ))
        return issues

    def _create_check(self, company_id, check_type, employee, message):
        return self.env['rn.hr.data.quality.check'].create({
            'name': message[:64],
            'check_type': check_type,
            'employee_id': employee.id,
            'message': message,
            'company_id': company_id,
        })
