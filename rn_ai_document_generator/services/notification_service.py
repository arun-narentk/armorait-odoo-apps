# -*- coding: utf-8 -*-
"""Notification hooks."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnAiDocumentNotificationService(models.AbstractModel):
    _name = 'rn.ai.document.notification.service'
    _description = 'AI Document Notification Service'

    def notify_generated(self, document):
        _logger.info('Document generated: %s', document.name)
        return True
