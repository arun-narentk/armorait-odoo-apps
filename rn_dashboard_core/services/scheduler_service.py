# -*- coding: utf-8 -*-
"""Cron jobs for snapshot cleanup and cache flush."""

import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnDashboardSchedulerService(models.AbstractModel):
    """Background maintenance for dashboard core."""

    _name = 'rn.dashboard.scheduler.service'
    _description = 'Dashboard Scheduler Service'

    def cron_cleanup_snapshots(self):
        for settings in self.env['rn.dashboard.settings'].search([]):
            days = settings.retention_days or 90
            cutoff = fields.Datetime.now() - timedelta(days=days)
            old = self.env['rn.dashboard.kpi.snapshot'].search([
                ('company_id', '=', settings.company_id.id),
                ('snapshot_at', '<', cutoff),
            ])
            count = len(old)
            old.unlink()
            _logger.info('Removed %s KPI snapshots older than %s days', count, days)
        return True

    def cron_clear_cache(self):
        return self.env['rn.dashboard.cache.service'].clear_prefix()
