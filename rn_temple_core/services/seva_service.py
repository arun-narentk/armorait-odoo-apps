# -*- coding: utf-8 -*-

from odoo import fields, models


class RnTempleSevaService(models.AbstractModel):
    _name = 'rn.temple.seva.service'
    _description = 'Seva Booking Service'

    def book_seva(self, devotee_id, seva_type_id, booking_date, slot_label=None):
        seva = self.env['rn.temple.seva.type'].browse(seva_type_id)
        booking = self.env['rn.temple.seva.booking'].create({
            'devotee_id': devotee_id,
            'seva_type_id': seva_type_id,
            'booking_date': booking_date,
            'slot_label': slot_label,
            'amount': seva.amount,
            'state': 'confirmed',
        })
        return booking.id

    def available_sevas_tomorrow(self, company_id=None):
        company_id = company_id or self.env.company.id
        return self.env['rn.temple.seva.type'].search([
            ('company_id', '=', company_id),
            ('active', '=', True),
        ])

    def slot_capacity_ok(self, seva_type_id, booking_date, slot_label):
        seva = self.env['rn.temple.seva.type'].browse(seva_type_id)
        count = self.env['rn.temple.seva.booking'].search_count([
            ('seva_type_id', '=', seva_type_id),
            ('booking_date', '=', booking_date),
            ('slot_label', '=', slot_label),
            ('state', 'in', ('draft', 'confirmed')),
        ])
        return count < (seva.capacity_per_slot or 1)
