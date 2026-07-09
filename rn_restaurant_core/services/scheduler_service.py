# -*- coding: utf-8 -*-
"""Background maintenance for restaurant core."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnRestaurantSchedulerService(models.AbstractModel):
    _name = 'rn.restaurant.scheduler.service'
    _description = 'Restaurant Scheduler Service'

    def cron_reset_dirty_tables(self):
        """Optional housekeeping: dirty tables older than room service can be auto-available later."""
        dirty = self.env['rn.restaurant.table'].search([('state', '=', 'dirty')], limit=200)
        _logger.info('Found %s dirty tables (no auto reset in Phase 1)', len(dirty))
        return True
