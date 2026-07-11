# -*- coding: utf-8 -*-
"""Department and trend payroll analytics."""

import logging
from datetime import timedelta

from odoo import fields, models

from .contract_compat import search_running_versions

_logger = logging.getLogger(__name__)


class RnHrPayrollAnalyticsService(models.AbstractModel):
    """Payroll trends and department breakdown."""

    _name = 'rn.hr.payroll.analytics.service'
    _description = 'Payroll Analytics Service'

    def get_department_costs(self, company_id=None):
        company_id = company_id or self.env.company.id
        departments = self.env['hr.department'].search([('company_id', '=', company_id)])
        result = []
        for dept in departments:
            contracts = search_running_versions(self.env, company_id, [
                ('employee_id.department_id', '=', dept.id),
            ])
            payroll = sum(contracts.mapped('wage'))
            ot = sum(self.env['rn.hr.overtime.log'].search([
                ('department_id', '=', dept.id),
                ('company_id', '=', company_id),
            ]).mapped('cost'))
            result.append({
                'department': dept.name,
                'headcount': len(contracts),
                'payroll': round(payroll, 2),
                'overtime': round(ot, 2),
                'total': round(payroll + ot, 2),
            })
        return sorted(result, key=lambda r: r['total'], reverse=True)

    def get_monthly_trend(self, company_id=None, months=6):
        company_id = company_id or self.env.company.id
        Snapshot = self.env['rn.hr.payroll.snapshot']
        today = fields.Date.context_today(self)
        trend = []
        for i in range(months - 1, -1, -1):
            period = (today.replace(day=1) - timedelta(days=30 * i))
            snap = Snapshot.search([
                ('company_id', '=', company_id),
                ('period', '<=', period),
                ('department_id', '=', False),
            ], order='period desc', limit=1)
            trend.append({
                'period': fields.Date.to_string(period)[:7],
                'gross': snap.gross_salary if snap else 0.0,
                'net': snap.net_salary if snap else 0.0,
            })
        return trend

    def refresh_monthly_snapshot(self, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        period = today.replace(day=1)
        summary = self.env['rn.hr.kpi.service'].get_executive_summary(company_id)
        Snapshot = self.env['rn.hr.payroll.snapshot']
        existing = Snapshot.search([
            ('company_id', '=', company_id),
            ('period', '=', period),
            ('department_id', '=', False),
        ], limit=1)
        vals = {
            'name': f'Payroll {period.strftime("%B %Y")}',
            'period': period,
            'gross_salary': summary['gross_salary'],
            'net_salary': summary['net_salary'],
            'overtime_cost': summary['overtime_cost'],
            'pf_contribution': summary['pf_contribution'],
            'esi_contribution': summary['esi_contribution'],
            'tds_amount': summary['tds_amount'],
            'headcount': summary['headcount'],
            'avg_salary': summary['avg_salary'],
            'company_id': company_id,
        }
        if existing:
            existing.write(vals)
        else:
            Snapshot.create(vals)
