# -*- coding: utf-8 -*-
"""Overtime tracking for cost analytics."""

from odoo import api, fields, models


class RnHrOvertimeLog(models.Model):
    """Overtime hours and cost per employee/department."""

    _name = 'rn.hr.overtime.log'
    _description = 'HR Overtime Log'
    _order = 'date desc'

    name = fields.Char(required=True)
    employee_id = fields.Many2one('hr.employee', required=True, index=True)
    department_id = fields.Many2one(related='employee_id.department_id', store=True)
    date = fields.Date(required=True, index=True)
    hours = fields.Float(required=True)
    hourly_rate = fields.Monetary(currency_field='currency_id')
    cost = fields.Monetary(compute='_compute_cost', store=True, currency_field='currency_id')
    note = fields.Text()
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('hours', 'hourly_rate')
    def _compute_cost(self):
        for rec in self:
            rec.cost = (rec.hours or 0.0) * (rec.hourly_rate or 0.0)
