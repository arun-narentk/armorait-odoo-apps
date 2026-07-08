# -*- coding: utf-8 -*-
"""GSTN JSON generation."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnGstJsonService(models.AbstractModel):
    """Build and validate GSTN-compatible JSON payloads."""

    _name = 'rn.gst.json.service'
    _description = 'GST JSON Service'

    def generate_json(self, gst_return):
        """Return JSON string for the return (Phase 4+)."""
        gst_return.ensure_one()
        _logger.info('JSON export placeholder for %s', gst_return.name)
        return {
            'ok': False,
            'json': '{}',
            'errors': ['JSON generator pending (Phase 4).'],
        }
