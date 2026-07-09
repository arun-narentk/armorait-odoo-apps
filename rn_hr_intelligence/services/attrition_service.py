# -*- coding: utf-8 -*-
"""Attrition and retention analytics."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnHrAttritionService(models.AbstractModel):
    """Turnover, hires, and retention metrics."""

    _name = 'rn.hr.attrition.service'
    _description = 'HR Attrition Service'

    def get_attrition_summary(self, company_id=None):
        company_id = company_id or self.env.company.id
        Employee = self.env['hr.employee'].with_context(active_test=False)
        active = Employee.search_count([('company_id', '=', company_id), ('active', '=', True)])
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)
        new_hires = Employee.search_count([
            ('company_id', '=', company_id),
            ('create_date', '>=', month_start),
        ])
        resignations = Employee.search_count([
            ('company_id', '=', company_id),
            ('active', '=', False),
            ('write_date', '>=', month_start),
        ])
        turnover = round(resignations / active * 100, 2) if active else 0.0
        return {
            'active_headcount': active,
            'new_hires': new_hires,
            'resignations': resignations,
            'turnover_rate': turnover,
            'retention_rate': round(100 - turnover, 2),
        }
