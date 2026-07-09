# -*- coding: utf-8 -*-
"""Overtime analytics."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnHrOvertimeService(models.AbstractModel):
    """Overtime hours, cost, and department leaders."""

    _name = 'rn.hr.overtime.service'
    _description = 'HR Overtime Service'

    def get_overtime_summary(self, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)
        logs = self.env['rn.hr.overtime.log'].search([
            ('company_id', '=', company_id),
            ('date', '>=', month_start),
        ])
        by_dept = {}
        for log in logs:
            dept = log.department_id.name or 'Unassigned'
            by_dept.setdefault(dept, {'hours': 0.0, 'cost': 0.0})
            by_dept[dept]['hours'] += log.hours
            by_dept[dept]['cost'] += log.cost
        top_depts = sorted(
            [{'department': k, **v} for k, v in by_dept.items()],
            key=lambda x: x['cost'],
            reverse=True,
        )[:5]
        return {
            'total_hours': round(sum(logs.mapped('hours')), 1),
            'total_cost': round(sum(logs.mapped('cost')), 2),
            'top_departments': top_depts,
        }

    def detect_excessive_overtime(self, company_id=None):
        company_id = company_id or self.env.company.id
        settings = self.env['rn.hr.intelligence.settings'].search(
            [('company_id', '=', company_id)], limit=1,
        )
        threshold = settings.overtime_threshold_hours if settings else 48.0
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)
        alerts = []
        employees = self.env['hr.employee'].search([('company_id', '=', company_id), ('active', '=', True)])
        for emp in employees:
            hours = sum(self.env['rn.hr.overtime.log'].search([
                ('employee_id', '=', emp.id),
                ('date', '>=', month_start),
            ]).mapped('hours'))
            if hours > threshold:
                alerts.append({'employee': emp.name, 'hours': hours})
        return alerts
