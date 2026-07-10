# -*- coding: utf-8 -*-
"""Executive workforce KPI calculations."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnHrKpiService(models.AbstractModel):
    """Compute headline HR and payroll KPIs."""

    _name = 'rn.hr.kpi.service'
    _description = 'HR KPI Service'

    def get_executive_summary(self, company_id=None):
        company_id = company_id or self.env.company.id
        employees = self.env['hr.employee'].search([
            ('company_id', '=', company_id),
            ('active', '=', True),
        ])
        contracts = self.env['hr.contract'].search([
            ('company_id', '=', company_id),
            ('state', '=', 'open'),
        ])
        gross = sum(contracts.mapped('wage'))
        settings = self._get_settings(company_id)
        pf = gross * (settings.pf_rate / 100.0) if settings else 0.0
        esi = gross * (settings.esi_rate / 100.0) if settings else 0.0
        ot_cost = sum(self.env['rn.hr.overtime.log'].search([
            ('company_id', '=', company_id),
            ('date', '>=', fields.Date.to_string(fields.Date.context_today(self))[:8] + '01'),
        ]).mapped('cost'))
        net_estimate = gross * 0.82
        return {
            'headcount': len(employees),
            'gross_salary': round(gross, 2),
            'net_salary': round(net_estimate, 2),
            'overtime_cost': round(ot_cost, 2),
            'pf_contribution': round(pf, 2),
            'esi_contribution': round(esi, 2),
            'tds_amount': round(gross * 0.05, 2),
            'bonus_amount': 0.0,
            'incentive_amount': 0.0,
            'avg_salary': round(gross / len(contracts), 2) if contracts else 0.0,
        }

    def get_attendance_cost_summary(self, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)
        attendances = self.env['hr.attendance'].search([
            ('employee_id.company_id', '=', company_id),
            ('check_in', '>=', month_start),
        ])
        leaves = self.env['hr.leave'].search([
            ('employee_id.company_id', '=', company_id),
            ('state', '=', 'validate'),
            ('date_from', '>=', month_start),
        ])
        return {
            'attendance_records': len(attendances),
            'leave_days': sum(leaves.mapped('number_of_days')),
            'late_arrivals': 0,
            'unpaid_days': 0,
        }

    def _get_settings(self, company_id):
        return self.env['rn.hr.intelligence.settings'].search(
            [('company_id', '=', company_id)], limit=1,
        )
