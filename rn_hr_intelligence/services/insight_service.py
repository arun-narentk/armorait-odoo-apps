# -*- coding: utf-8 -*-
"""AI-style workforce narrative."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnHrInsightService(models.AbstractModel):
    """Generate payroll and workforce summary narratives."""

    _name = 'rn.hr.insight.service'
    _description = 'HR Insight Service'

    def generate_payroll_summary(self, company_id=None):
        company_id = company_id or self.env.company.id
        kpi = self.env['rn.hr.kpi.service'].get_executive_summary(company_id)
        dept_costs = self.env['rn.hr.payroll.analytics.service'].get_department_costs(company_id)
        ot = self.env['rn.hr.overtime.service'].get_overtime_summary(company_id)
        attrition = self.env['rn.hr.attrition.service'].get_attrition_summary(company_id)

        lines = []
        lines.append(
            f'Estimated monthly gross payroll is {kpi["gross_salary"]:,.0f} '
            f'across {kpi["headcount"]} employees.'
        )
        if ot['total_cost'] > 0:
            top = ot['top_departments'][0]['department'] if ot['top_departments'] else 'operations'
            lines.append(
                f'Overtime cost this month is {ot["total_cost"]:,.0f}, '
                f'led by {top}.'
            )
        if dept_costs:
            lines.append(f'Highest payroll department is {dept_costs[0]["department"]}.')
        if attrition['resignations']:
            lines.append(
                f'{attrition["resignations"]} departures this month '
                f'(turnover {attrition["turnover_rate"]}%).'
            )

        html = '<p>' + ' '.join(lines) + '</p>'
        return self.env['rn.hr.ai.insight'].create({
            'name': f'Payroll Summary {fields.Date.context_today(self)}',
            'insight_type': 'payroll_summary',
            'summary_html': html,
            'period': fields.Date.context_today(self).replace(day=1),
            'company_id': company_id,
        })
