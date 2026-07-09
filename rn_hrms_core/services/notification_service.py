# -*- coding: utf-8 -*-
"""Email / WhatsApp / SMS notification stubs for HRMS."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnHrmsNotificationService(models.AbstractModel):
    """Queue HR notifications through configured channels."""

    _name = 'rn.hrms.notification.service'
    _description = 'HRMS Notification Service'

    def _settings(self, company_id):
        return self.env['rn.hrms.settings'].search([('company_id', '=', company_id)], limit=1)

    def notify_announcement(self, announcements):
        for rec in announcements:
            settings = self._settings(rec.company_id.id)
            if settings and settings.enable_email:
                rec.message_post(body='Announcement published and email notification queued.')
            _logger.info('Announcement notification %s', rec.name)
        return True

    def notify_approval_submitted(self, approval):
        approval.ensure_one()
        _logger.info('Approval submitted notification %s', approval.name)
        return True

    def notify_approval_decision(self, approval, approved=True):
        approval.ensure_one()
        _logger.info('Approval decision notification %s approved=%s', approval.name, approved)
        return True

    def notify_birthdays(self):
        """Cron stub for birthday wishes (full engine in companion modules)."""
        _logger.info('Birthday notification cron stub executed')
        return True
