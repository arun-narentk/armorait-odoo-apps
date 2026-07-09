# -*- coding: utf-8 -*-

from odoo import fields, models


class RnVetKennel(models.Model):
    _name = 'rn.vet.kennel'
    _description = 'Kennel'
    _order = 'name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    size = fields.Selection([('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')], default='medium')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
