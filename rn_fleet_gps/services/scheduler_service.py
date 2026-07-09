# -*- coding: utf-8 -*-
"""Cron orchestration."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnFleetSchedulerService(models.AbstractModel):
    _name = 'rn.fleet.scheduler.service'
    _description = 'Fleet Scheduler Service'

    def cron_poll_providers(self):
        devices = self.env['rn.fleet.gps.device'].search([
            ('state', '=', 'active'),
            ('provider', '!=', 'manual'),
        ])
        for device in devices:
            payload = self.env['rn.fleet.gps.provider.service'].fetch_latest(device)
            if payload:
                self.env['rn.fleet.location.service'].ingest(device, payload)
        _logger.info('Polled %s GPS devices', len(devices))
        return True

    def cron_auto_close_trips(self):
        return self.env['rn.fleet.trip.service'].cron_auto_close()

    def cron_offline_alerts(self):
        return self.env['rn.fleet.alert.service'].cron_offline_alerts()
