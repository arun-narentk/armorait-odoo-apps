# -*- coding: utf-8 -*-
"""Booking orchestration for create/confirm/reschedule."""

import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnBookingBookingService(models.AbstractModel):
    """High-level booking engine operations."""

    _name = 'rn.booking.booking.service'
    _description = 'Booking Engine Service'

    def create_appointment(self, vals):
        """Create draft/pending appointment with defaults from service."""
        service = self.env['rn.booking.service'].browse(vals['service_id'])
        if not vals.get('stop_datetime') and vals.get('start_datetime'):
            start = fields.Datetime.to_datetime(vals['start_datetime'])
            vals['stop_datetime'] = fields.Datetime.to_string(
                start + timedelta(minutes=service.duration_minutes or 30)
            )
        if not vals.get('amount_total'):
            vals['amount_total'] = service.list_price or 0.0
        if not vals.get('meeting_provider'):
            vals['meeting_provider'] = service.meeting_provider or 'none'
        if not vals.get('state'):
            vals['state'] = 'pending'
        appt = self.env['rn.booking.appointment'].create(vals)
        self.env['rn.booking.notification.service'].notify_confirmation(appt)
        _logger.info('Appointment created %s', appt.name)
        return appt

    def confirm_appointments(self, appointments):
        """Confirm and optionally open calendar event stub."""
        for appt in appointments:
            self.env['rn.booking.calendar.service'].ensure_calendar_event(appt)
            settings = self.env['rn.booking.settings'].search(
                [('company_id', '=', appt.company_id.id)], limit=1
            )
            if settings and settings.auto_invoice == 'on_booking':
                self.env['rn.booking.payment.service'].create_invoice(appt)
        return True

    def reschedule(self, appointment, start_datetime, stop_datetime=None):
        """Move an appointment to a new slot."""
        appointment.ensure_one()
        vals = {'start_datetime': start_datetime, 'state': 'confirmed'}
        if stop_datetime:
            vals['stop_datetime'] = stop_datetime
        else:
            start = fields.Datetime.to_datetime(start_datetime)
            vals['stop_datetime'] = fields.Datetime.to_string(
                start + timedelta(minutes=appointment.duration_minutes or 30)
            )
        appointment.write(vals)
        self.env['rn.booking.calendar.service'].ensure_calendar_event(appointment)
        self.env['rn.booking.notification.service'].notify_reschedule(appointment)
        return appointment
