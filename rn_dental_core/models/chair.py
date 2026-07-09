# -*- coding: utf-8 -*-

from odoo import fields, models


class RnDentalChair(models.Model):
    _name = 'rn.dental.chair'
    _description = 'Dental Chair'
    _order = 'name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
