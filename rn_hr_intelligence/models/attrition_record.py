# -*- coding: utf-8 -*-
"""Monthly attrition metrics."""

from odoo import fields, models


class RnHrAttritionRecord(models.Model):
    """Attrition and hiring statistics per period."""

    _name = 'rn.hr.attrition.record'
    _description = 'Attrition Record'
    _order = 'period desc'

    name = fields.Char(required=True)
    period = fields.Date(required=True, index=True)
    new_hires = fields.Integer()
    resignations = fields.Integer()
    headcount_start = fields.Integer()
    headcount_end = fields.Integer()
    turnover_rate = fields.Float(string='Turnover Rate %')
    retention_rate = fields.Float(string='Retention Rate %')
    department_id = fields.Many2one('hr.department')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
