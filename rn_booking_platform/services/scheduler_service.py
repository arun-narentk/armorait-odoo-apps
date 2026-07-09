# -*- coding: utf-8 -*-
"""Background jobs for reminders and cleanup."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnBookingSchedulerService(models.AbstractModel):
    """Cron entry points for the booking platform."""

    _name = 'rn.booking.scheduler.service'
    _description = 'Booking Scheduler Service'

    def cron_send_reminders(self):
        self.env['rn.booking.notification.service'].notify_reminders()
        return True

    def cron_mark_no_shows(self):
        """Mark past confirmed appointments still open as no-show candidates (Phase 1 stub)."""
        _logger.info('No-show cron stub executed')
        return True
