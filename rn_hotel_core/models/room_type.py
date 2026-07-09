# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHotelRoomType(models.Model):
    _name = 'rn.hotel.room.type'
    _description = 'Hotel Room Type'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    base_rate = fields.Float(string='Base Rate per Night', required=True)
    max_occupancy = fields.Integer(default=2)
    description = fields.Text()
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
