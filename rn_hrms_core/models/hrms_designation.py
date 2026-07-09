# -*- coding: utf-8 -*-
"""Job designations / positions."""

from odoo import fields, models


class RnHrmsDesignation(models.Model):
    """Designation independent from department for flexible org charts."""

    _name = 'rn.hrms.designation'
    _description = 'HRMS Designation'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    department_id = fields.Many2one('hr.department')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    description = fields.Text()
