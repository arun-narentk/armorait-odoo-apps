# -*- coding: utf-8 -*-
"""Workforce intelligence dashboard payload."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnHrDashboardService(models.AbstractModel):
    """Aggregate dashboard data for OWL client."""

    _name = 'rn.hr.dashboard.service'
    _description = 'HR Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        executive = self.env['rn.hr.kpi.service'].get_executive_summary(company_id)
        attendance = self.env['rn.hr.kpi.service'].get_attendance_cost_summary(company_id)
        overtime = self.env['rn.hr.overtime.service'].get_overtime_summary(company_id)
        attrition = self.env['rn.hr.attrition.service'].get_attrition_summary(company_id)
        departments = self.env['rn.hr.payroll.analytics.service'].get_department_costs(company_id)[:6]
        trend = self.env['rn.hr.payroll.analytics.service'].get_monthly_trend(company_id, months=6)
        quality_count = self.env['rn.hr.data.quality.check'].search_count([
            ('company_id', '=', company_id),
            ('resolved', '=', False),
        ])
        insight = self.env['rn.hr.ai.insight'].search([
            ('company_id', '=', company_id),
            ('insight_type', '=', 'payroll_summary'),
        ], limit=1)

        return {
            'executive': executive,
            'attendance': attendance,
            'overtime': overtime,
            'attrition': attrition,
            'departments': departments,
            'trend': trend,
            'quality_issues': quality_count,
            'ai_summary': insight.summary_html if insight else '',
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
