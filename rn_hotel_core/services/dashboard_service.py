# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHotelDashboardService(models.AbstractModel):
    _name = 'rn.hotel.dashboard.service'
    _description = 'Hotel Dashboard Service'

    def get_gm_dashboard(self, company_id=None):
        company_id = company_id or self.env.company.id
        Room = self.env['rn.hotel.room']
        Reservation = self.env['rn.hotel.reservation']
        Folio = self.env['rn.hotel.folio']
        today = fields.Date.context_today(self)

        rooms = Room.search([('company_id', '=', company_id), ('active', '=', True)])
        occupied = len(rooms.filtered(lambda r: r.status == 'occupied'))
        occupancy = round((occupied / len(rooms)) * 100, 1) if rooms else 0.0

        arrivals = Reservation.search_count([
            ('company_id', '=', company_id),
            ('check_in', '>=', fields.Datetime.to_datetime(today)),
            ('state', 'in', ('confirmed', 'checked_in')),
        ])
        departures = Reservation.search_count([
            ('company_id', '=', company_id),
            ('check_out', '>=', fields.Datetime.to_datetime(today)),
            ('state', 'checked_in'),
        ])
        revenue = sum(Folio.search([
            ('company_id', '=', company_id),
            ('open_date', '>=', fields.Datetime.to_datetime(today)),
        ]).mapped('amount_total'))

        dirty = len(rooms.filtered(lambda r: r.status in ('dirty', 'cleaning')))
        return {
            'occupancy_pct': occupancy,
            'occupied_rooms': occupied,
            'total_rooms': len(rooms),
            'arrivals_today': arrivals,
            'departures_today': departures,
            'revenue_today': revenue,
            'dirty_rooms': dirty,
            'adr': round(revenue / occupied, 2) if occupied else 0.0,
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }

    def get_room_board(self, company_id=None):
        company_id = company_id or self.env.company.id
        rooms = self.env['rn.hotel.room'].search([
            ('company_id', '=', company_id),
            ('active', '=', True),
        ], order='floor, name')
        return [
            {
                'id': r.id,
                'name': r.name,
                'floor': r.floor or '',
                'type': r.room_type_id.name,
                'status': r.status,
                'guest': r.current_reservation_id.guest_id.name if r.current_reservation_id else '',
            }
            for r in rooms
        ]
