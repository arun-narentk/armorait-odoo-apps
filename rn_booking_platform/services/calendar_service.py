# -*- coding: utf-8 -*-
"""Odoo calendar.event bridge (Google/Outlook sync later)."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnBookingCalendarService(models.AbstractModel):
    """Create or update a calendar.event for an appointment."""

    _name = 'rn.booking.calendar.service'
    _description = 'Booking Calendar Service'

    def ensure_calendar_event(self, appointment):
        """Link appointment to calendar.event for staff visibility."""
        appointment.ensure_one()
        Event = self.env['calendar.event']
        partner_ids = []
        if appointment.partner_id:
            partner_ids.append(appointment.partner_id.id)
        if appointment.staff_id and appointment.staff_id.partner_id:
            partner_ids.append(appointment.staff_id.partner_id.id)
        values = {
            'name': '%s - %s' % (appointment.name, appointment.service_id.name),
            'start': appointment.start_datetime,
            'stop': appointment.stop_datetime,
            'partner_ids': [(6, 0, list(set(partner_ids)))],
            'description': appointment.note or '',
        }
        if appointment.calendar_event_id:
            appointment.calendar_event_id.write(values)
            event = appointment.calendar_event_id
        else:
            event = Event.create(values)
            appointment.calendar_event_id = event.id
        _logger.info('Calendar event synced for %s', appointment.name)
        return event
