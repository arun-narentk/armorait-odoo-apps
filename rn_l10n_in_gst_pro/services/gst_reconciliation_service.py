# -*- coding: utf-8 -*-
"""Reconciliation runners."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnGstReconciliationService(models.AbstractModel):
    """Detect mismatches between books and GST return data."""

    _name = 'rn.gst.reconciliation.service'
    _description = 'GST Reconciliation Service'

    def run_reconciliation(self, reconciliation):
        """Populate mismatch lines (Phase 10)."""
        reconciliation.ensure_one()
        _logger.info('Reconciliation placeholder for %s', reconciliation.name)
        reconciliation.write({'state': 'done', 'mismatch_count': 0})
        return True
