# -*- coding: utf-8 -*-
"""OWL HR dashboard KPI aggregation."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnHrmsDashboardService(models.AbstractModel):
    """Build HRMS Core dashboard payload."""

    _name = 'rn.hrms.dashboard.service'
    _description = 'HRMS Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        Employee = self.env['hr.employee']
        employees = Employee.search([('company_id', '=', company_id)])
        pending = self.env['rn.hrms.approval'].search_count([
            ('company_id', '=', company_id),
            ('state', '=', 'pending'),
        ])
        announcements = self.env['rn.hrms.announcement'].search_count([
            ('company_id', '=', company_id),
            ('state', '=', 'published'),
        ])
        departments = len(employees.mapped('department_id'))
        return {
            'cards': {
                'employee_count': len(employees),
                'present_today': 0,
                'absent_today': 0,
                'late_arrivals': 0,
                'open_vacancies': 0,
                'new_hires': employees.filtered(
                    lambda e: e.rn_hrms_joining_date and e.rn_hrms_joining_date.month == fields.Date.context_today(self).month
                ).__len__(),
                'pending_approvals': pending,
                'announcements': announcements,
                'departments': departments,
                'payroll_cost': 0.0,
            },
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
