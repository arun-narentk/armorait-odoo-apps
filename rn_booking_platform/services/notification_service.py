# -*- coding: utf-8 -*-
"""Email / SMS / WhatsApp notification stubs."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnBookingNotificationService(models.AbstractModel):
    """Send booking lifecycle notifications through configured channels."""

    _name = 'rn.booking.notification.service'
    _description = 'Booking Notification Service'

    def _settings(self, company_id):
        return self.env['rn.booking.settings'].search(
            [('company_id', '=', company_id)], limit=1
        )

    def notify_confirmation(self, appointments):
        for appt in appointments:
            settings = self._settings(appt.company_id.id)
            if settings and settings.enable_email:
                appt.message_post(body='Booking confirmation queued for %s.' % appt.partner_id.name)
            _logger.info('Confirmation notification appointment=%s', appt.name)
        return True

    def notify_cancellation(self, appointments):
        for appt in appointments:
            appt.message_post(body='Cancellation notification queued.')
            _logger.info('Cancellation notification appointment=%s', appt.name)
        return True

    def notify_reschedule(self, appointments):
        for appt in appointments:
            appt.message_post(body='Reschedule notification queued.')
        return True

    def notify_reminders(self):
        """Cron entry: queue reminders for upcoming confirmed appointments."""
        # Full reminder engine arrives in Phase 7
        _logger.info('Reminder cron stub executed')
        return True
