# -*- coding: utf-8 -*-
"""Monthly payroll snapshot for analytics."""

from odoo import fields, models


class RnHrPayrollSnapshot(models.Model):
    """Stored monthly payroll aggregate."""

    _name = 'rn.hr.payroll.snapshot'
    _description = 'Payroll Snapshot'
    _order = 'period desc'

    name = fields.Char(required=True)
    period = fields.Date(required=True, index=True, string='Month')
    gross_salary = fields.Monetary(currency_field='currency_id')
    net_salary = fields.Monetary(currency_field='currency_id')
    overtime_cost = fields.Monetary(currency_field='currency_id')
    pf_contribution = fields.Monetary(string='PF Contribution', currency_field='currency_id')
    esi_contribution = fields.Monetary(string='ESI Contribution', currency_field='currency_id')
    tds_amount = fields.Monetary(string='TDS', currency_field='currency_id')
    bonus_amount = fields.Monetary(currency_field='currency_id')
    incentive_amount = fields.Monetary(currency_field='currency_id')
    headcount = fields.Integer()
    avg_salary = fields.Monetary(currency_field='currency_id')
    department_id = fields.Many2one('hr.department', string='Department')
    branch_id = fields.Many2one('res.partner', string='Branch', domain="[('is_company', '=', True)]")
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
