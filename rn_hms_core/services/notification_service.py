# -*- coding: utf-8 -*-
"""SMS / WhatsApp / Email notification stubs."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnHmsNotificationService(models.AbstractModel):
    """Queue appointment and operational notifications."""

    _name = 'rn.hms.notification.service'
    _description = 'HMS Notification Service'

    def notify_appointment_confirmed(self, appointments):
        for appt in appointments:
            appt.message_post(body='Appointment confirmation notification queued.')
            _logger.info('Appointment confirmed notice %s', appt.name)
        return True

    def notify_appointment_cancelled(self, appointments):
        for appt in appointments:
            appt.message_post(body='Appointment cancellation notification queued.')
        return True

    def notify_reminders(self):
        _logger.info('HMS appointment reminder cron stub executed')
        return True
