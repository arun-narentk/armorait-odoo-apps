# -*- coding: utf-8 -*-
"""Quick booking wizard for one asset."""

from datetime import timedelta

from odoo import fields, models


class RnRentalQuickBookingWizard(models.TransientModel):
    """Create a reserved booking for one asset."""

    _name = 'rn.rental.quick.booking.wizard'
    _description = 'Quick Rental Booking Wizard'

    partner_id = fields.Many2one('res.partner', required=True)
    asset_id = fields.Many2one('rn.rental.asset', required=True)
    date_start = fields.Datetime(required=True, default=fields.Datetime.now)
    date_end = fields.Datetime(
        required=True,
        default=lambda self: fields.Datetime.now() + timedelta(days=1),
    )
    plan = fields.Selection(
        selection=[
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='daily',
        required=True,
    )

    def action_create(self):
        self.ensure_one()
        booking = self.env['rn.rental.booking'].create({
            'partner_id': self.partner_id.id,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'plan': self.plan,
            'line_ids': [(0, 0, {'asset_id': self.asset_id.id})],
            'company_id': self.asset_id.company_id.id,
        })
        self.env['rn.rental.booking.service'].reserve(booking)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.rental.booking',
            'res_id': booking.id,
            'view_mode': 'form',
            'target': 'current',
        }
