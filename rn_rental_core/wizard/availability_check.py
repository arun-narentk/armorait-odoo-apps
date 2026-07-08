# -*- coding: utf-8 -*-
"""Check asset availability for a period."""

from odoo import fields, models


class RnRentalAvailabilityCheckWizard(models.TransientModel):
    """Quick availability probe for one asset."""

    _name = 'rn.rental.availability.check.wizard'
    _description = 'Rental Availability Check Wizard'

    asset_id = fields.Many2one('rn.rental.asset', required=True)
    date_start = fields.Datetime(required=True, default=fields.Datetime.now)
    date_end = fields.Datetime(required=True)
    result = fields.Text(readonly=True)

    def action_check(self):
        self.ensure_one()
        available = self.env['rn.rental.availability.service'].is_available(
            self.asset_id, self.date_start, self.date_end
        )
        quote = self.env['rn.rental.pricing.service'].quote_asset(
            self.asset_id,
            plan='daily',
            date_start=self.date_start,
            date_end=self.date_end,
        )
        self.result = 'Available: %s | Unit Price: %s | Duration: %s | Subtotal: %s' % (
            available,
            quote['unit_price'],
            quote['duration'],
            quote['subtotal'],
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.rental.availability.check.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
