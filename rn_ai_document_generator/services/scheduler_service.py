# -*- coding: utf-8 -*-
"""Maintenance crons."""

import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnAiDocumentSchedulerService(models.AbstractModel):
    _name = 'rn.ai.document.scheduler.service'
    _description = 'AI Document Scheduler Service'

    def cron_cleanup_old_versions(self):
        cutoff = fields.Datetime.now() - timedelta(days=365)
        # Keep at least latest 3 versions per document; prune very old extras later
        old = self.env['rn.ai.document.version'].search([
            ('create_date', '<', cutoff),
        ], limit=200)
        _logger.info('Version cleanup scan found %s old rows (retained for audit in Phase 1)', len(old))
        return True
