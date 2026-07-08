# -*- coding: utf-8 -*-
"""Notification hooks for CRM Ultimate Pro."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnCrmNotificationService(models.AbstractModel):
    """Notify users about scoring, duplicates, and follow-ups."""

    _name = 'rn.crm.notification.service'
    _description = 'CRM Notification Service'

    def notify(self, event_type, payload=None):
        """Queue notification for an event (mail/activity/whatsapp hook)."""
        _logger.info('CRM notify %s keys=%s', event_type, list((payload or {}).keys()))
        return True
