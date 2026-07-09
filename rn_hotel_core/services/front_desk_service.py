# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.exceptions import UserError


class RnHotelFrontDeskService(models.AbstractModel):
    _name = 'rn.hotel.front.desk.service'
    _description = 'Front Desk Service'

    def check_in(self, reservation_id, room_id=None):
        res = self.env['rn.hotel.reservation'].browse(reservation_id)
        if not res.exists() or res.state not in ('draft', 'confirmed'):
            raise UserError('Reservation cannot be checked in.')
        room = self.env['rn.hotel.room'].browse(room_id or res.room_id.id)
        if not room.exists() or room.status not in ('vacant', 'reserved'):
            raise UserError('Room not available for check-in.')
        folio = self.env['rn.hotel.folio'].create({
            'guest_id': res.guest_id.id,
            'reservation_id': res.id,
            'room_id': room.id,
        })
        nights = max((res.check_out.date() - res.check_in.date()).days, 1)
        rate = res.rate_per_night or res.room_type_id.base_rate
        self.env['rn.hotel.folio.line'].create({
            'folio_id': folio.id,
            'charge_type': 'room',
            'description': f'Room {room.name} ({nights} night(s))',
            'quantity': nights,
            'unit_price': rate,
        })
        room.write({'status': 'occupied', 'current_reservation_id': res.id})
        res.write({'room_id': room.id, 'folio_id': folio.id, 'state': 'checked_in'})
        return folio.id

    def check_out(self, reservation_id):
        res = self.env['rn.hotel.reservation'].browse(reservation_id)
        if not res.exists() or res.state != 'checked_in':
            raise UserError('Guest is not checked in.')
        folio = res.folio_id
        if folio and folio.state == 'open':
            folio.write({'state': 'closed', 'close_date': fields.Datetime.now()})
        if res.room_id:
            settings = res.company_id._get_hotel_settings()
            new_status = 'dirty' if settings.auto_dirty_on_checkout else 'vacant'
            res.room_id.write({
                'status': new_status,
                'current_reservation_id': False,
            })
            if new_status == 'dirty':
                self.env['rn.hotel.housekeeping.service'].create_task_from_checkout(res.room_id.id)
        res.state = 'checked_out'
        return folio.id if folio else False
