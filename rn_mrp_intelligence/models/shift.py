# -*- coding: utf-8 -*-
"""Production shift definitions."""

from odoo import fields, models


class RnMrpShift(models.Model):
    """Factory shift for production comparison."""

    _name = 'rn.mrp.shift'
    _description = 'Manufacturing Shift'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    time_start = fields.Float(string='Start Hour', help='0-24 decimal hours')
    time_end = fields.Float(string='End Hour')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    _shift_code_company_uniq = models.Constraint(
        'unique(code, company_id)',
        'Shift code must be unique per company.',
    )
