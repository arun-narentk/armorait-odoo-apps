# -*- coding: utf-8 -*-
"""Scheduled duplicate scans."""

from odoo import models


class RnDupSchedulerService(models.AbstractModel):
    _name = 'rn.dup.scheduler.service'
    _description = 'Duplicate Finder Scheduler'

    def cron_run_auto_scans(self):
        self.env['rn.dup.scan.service'].cron_run_auto_scans()
