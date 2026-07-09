# -*- coding: utf-8 -*-
"""Background jobs for Hospital ERP core."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnHmsSchedulerService(models.AbstractModel):
    """Cron entry points."""

    _name = 'rn.hms.scheduler.service'
    _description = 'HMS Scheduler Service'

    def cron_appointment_reminders(self):
        self.env['rn.hms.notification.service'].notify_reminders()
        return True
