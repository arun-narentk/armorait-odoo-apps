# -*- coding: utf-8 -*-
"""Notification hooks for dashboard alerts."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnDashboardNotificationService(models.AbstractModel):
    """Email / activity notification stubs for Phase 1."""

    _name = 'rn.dashboard.notification.service'
    _description = 'Dashboard Notification Service'

    def notify_alert(self, alert):
        alert.ensure_one()
        _logger.info('Dashboard alert notification: %s (%s)', alert.name, alert.severity)
        # WhatsApp / SMS / Teams / Slack reserved for companion connectors
        return True
