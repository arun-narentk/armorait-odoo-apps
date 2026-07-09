# -*- coding: utf-8 -*-
"""Notification stubs for restaurant suite."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnRestaurantNotificationService(models.AbstractModel):
    _name = 'rn.restaurant.notification.service'
    _description = 'Restaurant Notification Service'

    def notify_low_menu_items(self, items):
        _logger.info('Low/out menu notification placeholder for %s items', len(items))
        return True
