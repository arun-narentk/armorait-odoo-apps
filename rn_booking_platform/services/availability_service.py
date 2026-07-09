# -*- coding: utf-8 -*-
"""Slot availability engine (Phase 1 rule-based)."""

import logging
from datetime import datetime, timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnBookingAvailabilityService(models.AbstractModel):
    """Compute free slots from working hours and existing appointments."""

    _name = 'rn.booking.availability.service'
    _description = 'Booking Availability Service'

    def get_slots(self, service, staff=None, location=None, day=None, slot_minutes=None):
        """Return list of available start datetimes for a day."""
        service.ensure_one()
        day = day or fields.Date.context_today(self)
        settings = self.env['rn.booking.settings'].search(
            [('company_id', '=', service.company_id.id)], limit=1
        )
        interval = slot_minutes or (settings.slot_interval_minutes if settings else 15)
        duration = service.duration_minutes or 30
        buffer_before = service.buffer_before or 0
        buffer_after = service.buffer_after or 0

        staff = staff or service.staff_ids[:1]
        hours = staff.working_hour_ids.filtered(
            lambda h: h.dayofweek == str(day.weekday())
        ) if staff else self.env['rn.booking.working.hour']
        if not hours:
            # Default 09:00-17:00 when no hours configured
            hours = self.env['rn.booking.working.hour'].new({
                'dayofweek': str(day.weekday()),
                'hour_from': 9.0,
                'hour_to': 17.0,
            })

        busy = self.env['rn.booking.appointment'].search([
            ('state', 'in', ('pending', 'confirmed', 'done')),
            ('start_datetime', '>=', fields.Datetime.to_string(datetime.combine(day, datetime.min.time()))),
            ('start_datetime', '<', fields.Datetime.to_string(datetime.combine(day + timedelta(days=1), datetime.min.time()))),
            ('company_id', '=', service.company_id.id),
        ])
        if staff:
            busy = busy.filtered(lambda a: not a.staff_id or a.staff_id == staff)

        slots = []
        for hour in hours:
            start_min = int(hour.hour_from * 60)
            end_min = int(hour.hour_to * 60)
            cursor = start_min
            while cursor + duration <= end_min:
                slot_start = datetime.combine(day, datetime.min.time()) + timedelta(minutes=cursor)
                slot_stop = slot_start + timedelta(minutes=duration)
                padded_start = slot_start - timedelta(minutes=buffer_before)
                padded_stop = slot_stop + timedelta(minutes=buffer_after)
                conflict = False
                for appt in busy:
                    if appt.start_datetime < padded_stop and appt.stop_datetime > padded_start:
                        conflict = True
                        break
                if not conflict:
                    slots.append({
                        'start': fields.Datetime.to_string(slot_start),
                        'stop': fields.Datetime.to_string(slot_stop),
                        'staff_id': staff.id if staff else False,
                        'location_id': location.id if location else False,
                    })
                cursor += max(interval, 5)
        _logger.info('Availability slots=%s service=%s day=%s', len(slots), service.id, day)
        return slots
