# -*- coding: utf-8 -*-

from odoo import fields, models


class RnDentalProcedure(models.Model):
    _name = 'rn.dental.procedure'
    _description = 'Dental Procedure'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    category = fields.Selection(
        [
            ('preventive', 'Preventive'),
            ('restorative', 'Restorative'),
            ('endodontic', 'Endodontic'),
            ('prosthetic', 'Prosthetic'),
            ('orthodontic', 'Orthodontic'),
            ('surgical', 'Surgical'),
            ('cosmetic', 'Cosmetic'),
        ],
        default='restorative',
    )
    default_duration_minutes = fields.Integer(default=30)
    list_price = fields.Float(string='Default Fee')
    product_id = fields.Many2one('product.product')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
