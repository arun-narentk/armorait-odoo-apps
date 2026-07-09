# -*- coding: utf-8 -*-
"""Rental asset categories."""

from odoo import fields, models


class RnRentalCategory(models.Model):
    """Neutral category for rentable assets."""

    _name = 'rn.rental.category'
    _description = 'Rental Category'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    parent_id = fields.Many2one('rn.rental.category', string='Parent')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Text()
