# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHotelRoomServiceOrder(models.Model):
    _name = 'rn.hotel.room.service.order'
    _description = 'Room Service Order'
    _order = 'order_time desc'

    name = fields.Char(required=True)
    folio_id = fields.Many2one('rn.hotel.folio', required=True, index=True)
    room_id = fields.Many2one(related='folio_id.room_id', store=True)
    order_time = fields.Datetime(default=fields.Datetime.now)
    state = fields.Selection(
        [('new', 'New'), ('preparing', 'Preparing'), ('delivered', 'Delivered'), ('billed', 'Billed')],
        default='new',
    )
    note = fields.Text()
    amount = fields.Float()
    company_id = fields.Many2one(related='folio_id.company_id', store=True, index=True)
