# -*- coding: utf-8 -*-
"""Configurable abbreviation expansion."""

from odoo import fields, models


class RnNameAbbreviation(models.Model):
    _name = 'rn.name.abbreviation'
    _description = 'Name Abbreviation'
    _order = 'short_form'

    active = fields.Boolean(default=True)
    short_form = fields.Char(required=True)
    expansion = fields.Char(required=True)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )

    _sql_constraints = [
        (
            'short_form_company_uniq',
            'unique(short_form, company_id)',
            'Abbreviation already exists for this company.',
        ),
    ]
