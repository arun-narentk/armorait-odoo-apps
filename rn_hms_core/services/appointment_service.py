# -*- coding: utf-8 -*-
"""Appointment confirmation and calendar bridge."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnHmsAppointmentService(models.AbstractModel):
    """Confirm appointments and sync calendar.event."""

    _name = 'rn.hms.appointment.service'
    _description = 'HMS Appointment Service'

    def confirm(self, appointments):
        for appt in appointments:
            if not appt.token_number:
                settings = self.env['rn.hms.settings'].search(
                    [('company_id', '=', appt.company_id.id)], limit=1
                )
                if not settings or settings.enable_token:
                    appt.token_number = self.env['ir.sequence'].next_by_code('rn.hms.token') or False
            appt.state = 'confirmed'
            self._ensure_calendar_event(appt)
            self.env['rn.hms.notification.service'].notify_appointment_confirmed(appt)
        _logger.info('Confirmed %s appointments', len(appointments))
        return True

    def _ensure_calendar_event(self, appt):
        Event = self.env['calendar.event']
        partner_ids = []
        if appt.patient_id.partner_id:
            partner_ids.append(appt.patient_id.partner_id.id)
        if appt.doctor_id.partner_id:
            partner_ids.append(appt.doctor_id.partner_id.id)
        values = {
            'name': '%s - %s' % (appt.name, appt.patient_id.name),
            'start': appt.start_datetime,
            'stop': appt.stop_datetime,
            'partner_ids': [(6, 0, list(set(partner_ids)))],
            'description': appt.chief_complaint or '',
        }
        if appt.calendar_event_id:
            appt.calendar_event_id.write(values)
        else:
            appt.calendar_event_id = Event.create(values).id
        return True
