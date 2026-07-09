# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnHotelFolioLine(models.Model):
    _name = 'rn.hotel.folio.line'
    _description = 'Folio Charge Line'
    _order = 'charge_date desc'

    folio_id = fields.Many2one('rn.hotel.folio', required=True, ondelete='cascade', index=True)
    charge_type = fields.Selection(
        [
            ('room', 'Room Charge'),
            ('restaurant', 'Restaurant'),
            ('room_service', 'Room Service'),
            ('minibar', 'Minibar'),
            ('laundry', 'Laundry'),
            ('other', 'Other'),
        ],
        default='room',
        required=True,
    )
    description = fields.Char(required=True)
    product_id = fields.Many2one('product.product')
    quantity = fields.Float(default=1.0)
    unit_price = fields.Float(required=True)
    amount = fields.Float(compute='_compute_amount', store=True)
    charge_date = fields.Datetime(default=fields.Datetime.now)
    company_id = fields.Many2one(related='folio_id.company_id', store=True, index=True)

    @api.depends('quantity', 'unit_price')
    def _compute_amount(self):
        for line in self:
            line.amount = (line.quantity or 0.0) * (line.unit_price or 0.0)
