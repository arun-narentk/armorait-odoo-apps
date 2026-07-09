# -*- coding: utf-8 -*-
"""Cron jobs for CRM Ultimate Pro."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnCrmSchedulerService(models.AbstractModel):
    """Periodic scoring, follow-ups, duplicate scans, and snapshots."""

    _name = 'rn.crm.scheduler.service'
    _description = 'CRM Scheduler Service'

    def cron_recompute_scores(self):
        leads = self.env['crm.lead'].search([('active', '=', True)], limit=500)
        self.env['rn.crm.lead.scoring.service'].recompute_scores(leads)
        return True

    def cron_followups(self):
        self.env['rn.crm.followup.service'].run_rules()
        return True

    def cron_duplicate_scan(self):
        self.env['rn.crm.duplicate.service'].scan_leads()
        return True

    def cron_dashboard_snapshot(self):
        self.env['rn.crm.dashboard.service'].create_snapshot()
        return True
