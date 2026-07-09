# -*- coding: utf-8 -*-
"""HR data quality flags."""

from odoo import fields, models


class RnHrDataQualityCheck(models.Model):
    """Data completeness issue for HR analytics."""

    _name = 'rn.hr.data.quality.check'
    _description = 'HR Data Quality Check'
    _order = 'create_date desc'

    name = fields.Char(required=True)
    check_type = fields.Selection(
        selection=[
            ('missing_contract', 'Missing Contract'),
            ('missing_department', 'Missing Department'),
            ('missing_attendance', 'Incomplete Attendance'),
            ('missing_cost_center', 'Missing Cost Center'),
            ('duplicate_allowance', 'Duplicate Allowance'),
        ],
        required=True,
    )
    employee_id = fields.Many2one('hr.employee')
    message = fields.Text(required=True)
    resolved = fields.Boolean(default=False)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
