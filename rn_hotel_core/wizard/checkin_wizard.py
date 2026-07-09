# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHotelCheckinWizard(models.TransientModel):
    _name = 'rn.hotel.checkin.wizard'
    _description = 'Check-in Wizard'

    reservation_id = fields.Many2one('rn.hotel.reservation', required=True)
    room_id = fields.Many2one('rn.hotel.room', required=True)
    id_verified = fields.Boolean(string='ID Verified')

    def action_check_in(self):
        self.ensure_one()
        folio_id = self.env['rn.hotel.front.desk.service'].check_in(
            self.reservation_id.id,
            room_id=self.room_id.id,
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.hotel.folio',
            'res_id': folio_id,
            'view_mode': 'form',
            'target': 'current',
        }
