# -*- coding: utf-8 -*-
"""Cancellation wizard with reason."""

from odoo import fields, models


class RnBookingCancelWizard(models.TransientModel):
    """Capture cancel reason then cancel appointment."""

    _name = 'rn.booking.cancel.wizard'
    _description = 'Cancel Appointment Wizard'

    appointment_id = fields.Many2one('rn.booking.appointment', required=True)
    cancel_reason = fields.Text(required=True)

    def action_cancel(self):
        self.ensure_one()
        self.appointment_id.write({'cancel_reason': self.cancel_reason, 'state': 'cancel'})
        self.env['rn.booking.notification.service'].notify_cancellation(self.appointment_id)
        return {'type': 'ir.actions.act_window_close'}
