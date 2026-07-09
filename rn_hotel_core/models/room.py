# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHotelRoom(models.Model):
    _name = 'rn.hotel.room'
    _description = 'Hotel Room'
    _inherit = ['mail.thread']
    _order = 'floor, name'

    name = fields.Char(required=True, string='Room Number')
    room_type_id = fields.Many2one('rn.hotel.room.type', required=True, index=True)
    floor = fields.Char()
    status = fields.Selection(
        [
            ('vacant', 'Vacant'),
            ('occupied', 'Occupied'),
            ('dirty', 'Dirty'),
            ('cleaning', 'Cleaning'),
            ('maintenance', 'Maintenance'),
            ('reserved', 'Reserved'),
            ('blocked', 'Blocked'),
        ],
        default='vacant',
        required=True,
        tracking=True,
        index=True,
    )
    current_reservation_id = fields.Many2one('rn.hotel.reservation', copy=False)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)', 'Room number must be unique per property.'),
    ]
