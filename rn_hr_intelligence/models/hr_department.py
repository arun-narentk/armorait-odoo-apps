# -*- coding: utf-8 -*-

from odoo import fields, models


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    rn_payroll_budget = fields.Monetary(
        string='Monthly Payroll Budget',
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
    )
