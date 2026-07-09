# -*- coding: utf-8 -*-

from odoo import fields, models


class RnTempleSevaType(models.Model):
    _name = 'rn.temple.seva.type'
    _description = 'Seva Type'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    description = fields.Text()
    amount = fields.Float(string='Suggested Amount')
    duration_minutes = fields.Integer(default=30)
    capacity_per_slot = fields.Integer(default=5, string='Capacity per Slot')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
