# -*- coding: utf-8 -*-
"""Quick booking wizard for backend users."""

from datetime import timedelta

from odoo import fields, models


class RnBookingQuickCreateWizard(models.TransientModel):
    """Create an appointment from service + slot inputs."""

    _name = 'rn.booking.quick.create.wizard'
    _description = 'Quick Booking Wizard'

    partner_id = fields.Many2one('res.partner', required=True)
    service_id = fields.Many2one('rn.booking.service', required=True)
    staff_id = fields.Many2one('rn.booking.staff')
    location_id = fields.Many2one('rn.booking.location')
    start_datetime = fields.Datetime(required=True, default=fields.Datetime.now)
    note = fields.Text()

    def action_create(self):
        self.ensure_one()
        service = self.service_id
        stop = fields.Datetime.to_datetime(self.start_datetime) + timedelta(
            minutes=service.duration_minutes or 30
        )
        appt = self.env['rn.booking.booking.service'].create_appointment({
            'partner_id': self.partner_id.id,
            'service_id': service.id,
            'staff_id': self.staff_id.id if self.staff_id else False,
            'location_id': self.location_id.id if self.location_id else False,
            'start_datetime': self.start_datetime,
            'stop_datetime': fields.Datetime.to_string(stop),
            'booking_source': 'backend',
            'note': self.note,
            'company_id': service.company_id.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.booking.appointment',
            'res_id': appt.id,
            'view_mode': 'form',
            'target': 'current',
        }
