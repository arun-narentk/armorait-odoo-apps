# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnHotelReservation(models.Model):
    _name = 'rn.hotel.reservation'
    _description = 'Hotel Reservation'
    _inherit = ['mail.thread']
    _order = 'check_in desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    guest_id = fields.Many2one('rn.hotel.guest', required=True, index=True)
    room_type_id = fields.Many2one('rn.hotel.room.type', required=True)
    room_id = fields.Many2one('rn.hotel.room', index=True)
    booking_type = fields.Selection(
        [
            ('online', 'Online'),
            ('walkin', 'Walk-in'),
            ('corporate', 'Corporate'),
            ('group', 'Group'),
        ],
        default='walkin',
    )
    check_in = fields.Datetime(required=True, index=True)
    check_out = fields.Datetime(required=True, index=True)
    adults = fields.Integer(default=1)
    children = fields.Integer()
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('checked_in', 'Checked In'),
            ('checked_out', 'Checked Out'),
            ('cancelled', 'Cancelled'),
            ('no_show', 'No Show'),
        ],
        default='draft',
        required=True,
        tracking=True,
    )
    rate_per_night = fields.Float()
    folio_id = fields.Many2one('rn.hotel.folio', copy=False)
    source = fields.Char(string='Booking Source')
    note = fields.Text()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('rn.hotel.reservation') or 'RES'
        return super().create(vals_list)

    def action_confirm(self):
        for res in self:
            if res.room_id:
                res.room_id.write({'status': 'reserved', 'current_reservation_id': res.id})
        self.write({'state': 'confirmed'})

    def action_cancel(self):
        for res in self:
            if res.room_id and res.room_id.status == 'reserved':
                res.room_id.write({'status': 'vacant', 'current_reservation_id': False})
        self.write({'state': 'cancelled'})
