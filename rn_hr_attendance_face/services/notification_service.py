# -*- coding: utf-8 -*-
"""HR / manager / employee notifications."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnHrFaceNotificationService(models.AbstractModel):
    """Notify stakeholders of attendance and security events."""

    _name = 'rn.hr.face.notification.service'
    _description = 'Face Attendance Notification Service'

    def notify_event(self, event_type, payload=None):
        """Queue chatter or mail notifications for key events."""
        # Phase 9/10: mail templates and activities.
        _logger.info('Face attendance notify %s payload_keys=%s', event_type, list((payload or {}).keys()))
        return True
