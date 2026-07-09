# -*- coding: utf-8 -*-
"""Lean rental booking for core availability engine."""

from odoo import api, fields, models


class RnRentalBooking(models.Model):
    """Booking / reservation used by availability and pricing engines."""

    _name = 'rn.rental.booking'
    _description = 'Rental Booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, id desc'

    name = fields.Char(required=True, copy=False, default='New', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True, index=True)
    date_start = fields.Datetime(required=True, index=True, tracking=True)
    date_end = fields.Datetime(required=True, index=True, tracking=True)
    plan = fields.Selection(
        selection=[
            ('hourly', 'Hourly'),
            ('half_day', 'Half Day'),
            ('daily', 'Daily'),
            ('weekend', 'Weekend'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ],
        default='daily',
        required=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('reserved', 'Reserved'),
            ('confirmed', 'Confirmed'),
            ('picked_up', 'Picked Up'),
            ('returned', 'Returned'),
            ('done', 'Completed'),
            ('cancel', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
        index=True,
    )
    payment_state = fields.Selection(
        selection=[
            ('not_paid', 'Not Paid'),
            ('partial', 'Partial'),
            ('paid', 'Paid'),
            ('refunded', 'Refunded'),
        ],
        default='not_paid',
        tracking=True,
    )
    line_ids = fields.One2many('rn.rental.booking.line', 'booking_id', string='Lines')
    amount_untaxed = fields.Monetary(compute='_compute_amounts', store=True, currency_field='currency_id')
    deposit_amount = fields.Monetary(currency_field='currency_id')
    amount_total = fields.Monetary(compute='_compute_amounts', store=True, currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Html()

    @api.depends('line_ids.subtotal', 'deposit_amount')
    def _compute_amounts(self):
        for booking in self:
            untaxed = sum(booking.line_ids.mapped('subtotal'))
            booking.amount_untaxed = untaxed
            booking.amount_total = untaxed

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rn.rental.booking') or 'New'
        return super().create(vals_list)

    def action_check_availability(self):
        return self.env['rn.rental.availability.service'].validate_booking(self)

    def action_reserve(self):
        return self.env['rn.rental.booking.service'].reserve(self)

    def action_confirm(self):
        return self.env['rn.rental.booking.service'].confirm(self)

    def action_cancel(self):
        return self.env['rn.rental.booking.service'].cancel(self)

    def action_recompute_prices(self):
        return self.env['rn.rental.pricing.service'].recompute_booking(self)
