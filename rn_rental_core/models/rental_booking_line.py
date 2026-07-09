# -*- coding: utf-8 -*-
"""Booking lines for rentable assets."""

from odoo import api, fields, models


class RnRentalBookingLine(models.Model):
    """One asset rented on a booking."""

    _name = 'rn.rental.booking.line'
    _description = 'Rental Booking Line'
    _order = 'id'

    booking_id = fields.Many2one('rn.rental.booking', required=True, ondelete='cascade', index=True)
    asset_id = fields.Many2one('rn.rental.asset', required=True, index=True)
    plan = fields.Selection(related='booking_id.plan', store=True)
    date_start = fields.Datetime(related='booking_id.date_start', store=True)
    date_end = fields.Datetime(related='booking_id.date_end', store=True)
    unit_price = fields.Monetary(currency_field='currency_id')
    quantity = fields.Float(default=1.0)
    duration = fields.Float(string='Duration Units', default=1.0)
    subtotal = fields.Monetary(compute='_compute_subtotal', store=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='booking_id.currency_id', store=True)
    company_id = fields.Many2one(related='booking_id.company_id', store=True, index=True)

    @api.depends('unit_price', 'quantity', 'duration')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = (line.unit_price or 0.0) * (line.quantity or 0.0) * (line.duration or 0.0)

    @api.onchange('asset_id', 'plan', 'date_start', 'date_end')
    def _onchange_pricing(self):
        for line in self:
            if not line.asset_id or not line.booking_id:
                continue
            price_info = self.env['rn.rental.pricing.service'].quote_asset(
                line.asset_id,
                plan=line.plan or 'daily',
                date_start=line.date_start,
                date_end=line.date_end,
            )
            line.unit_price = price_info['unit_price']
            line.duration = price_info['duration']
