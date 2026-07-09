# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.exceptions import UserError


class RnHotelReservationService(models.AbstractModel):
    _name = 'rn.hotel.reservation.service'
    _description = 'Reservation Service'

    def create_reservation(self, guest_id, room_type_id, check_in, check_out, room_id=None, **kwargs):
        guest = self.env['rn.hotel.guest'].browse(guest_id)
        room_type = self.env['rn.hotel.room.type'].browse(room_type_id)
        if not guest.exists() or not room_type.exists():
            raise UserError('Guest and room type are required.')
        if room_id:
            room = self.env['rn.hotel.room'].browse(room_id)
            if room.status not in ('vacant', 'reserved'):
                raise UserError('Selected room is not available.')
        return self.env['rn.hotel.reservation'].create({
            'guest_id': guest.id,
            'room_type_id': room_type.id,
            'room_id': room_id,
            'check_in': check_in,
            'check_out': check_out,
            'rate_per_night': kwargs.get('rate') or room_type.base_rate,
            'booking_type': kwargs.get('booking_type', 'walkin'),
            'source': kwargs.get('source', ''),
            'state': 'confirmed' if room_id else 'draft',
        }).id

    def find_available_rooms(self, room_type_id, check_in, check_out):
        rooms = self.env['rn.hotel.room'].search([
            ('room_type_id', '=', room_type_id),
            ('status', 'in', ('vacant', 'reserved')),
            ('company_id', '=', self.env.company.id),
        ])
        return rooms.ids
