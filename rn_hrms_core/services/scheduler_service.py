# -*- coding: utf-8 -*-
"""Background jobs for HRMS core."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnHrmsSchedulerService(models.AbstractModel):
    """Cron entry points for core HRMS automation."""

    _name = 'rn.hrms.scheduler.service'
    _description = 'HRMS Scheduler Service'

    def cron_birthday_wishes(self):
        self.env['rn.hrms.notification.service'].notify_birthdays()
        return True

    def cron_expire_announcements(self):
        day = fields.Date.context_today(self)
        outdated = self.env['rn.hrms.announcement'].search([
            ('state', '=', 'published'),
            ('date_end', '!=', False),
            ('date_end', '<', day),
        ])
        outdated.write({'state': 'done'})
        _logger.info('Expired %s announcements', len(outdated))
        return True
