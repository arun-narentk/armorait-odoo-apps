# -*- coding: utf-8 -*-
"""Configurable industries for white-label booking."""

from odoo import fields, models


class RnBookingIndustry(models.Model):
    """Industry template that drives labels and default booking behavior."""

    _name = 'rn.booking.industry'
    _description = 'Booking Industry'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Text()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    _code_uniq = models.Constraint(
        'unique(code)',
        'Industry code must be unique.',
    )
