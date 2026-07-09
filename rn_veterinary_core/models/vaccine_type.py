# -*- coding: utf-8 -*-

from odoo import fields, models


class RnVetVaccineType(models.Model):
    _name = 'rn.vet.vaccine.type'
    _description = 'Vaccine Type'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    species = fields.Selection(
        [
            ('dog', 'Dog'),
            ('cat', 'Cat'),
            ('bird', 'Bird'),
            ('all', 'All Species'),
        ],
        default='dog',
    )
    interval_months = fields.Integer(default=12, string='Booster Interval (months)')
    product_id = fields.Many2one('product.product')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
