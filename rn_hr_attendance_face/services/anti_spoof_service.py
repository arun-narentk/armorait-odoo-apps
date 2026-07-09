# -*- coding: utf-8 -*-
"""Liveness / anti-spoof checks."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnHrAntiSpoofService(models.AbstractModel):
    """Reject printed photos, screens, and replay attacks."""

    _name = 'rn.hr.anti.spoof.service'
    _description = 'Face Anti Spoof Service'

    def analyze(self, frames, enabled=True):
        """Return liveness score and spoof classification."""
        if not enabled:
            return {'ok': True, 'is_live': True, 'score': 1.0, 'labels': []}
        # Phase 6: blink, head motion, texture / depth heuristics.
        _logger.debug('anti_spoof analyze frames=%s', len(frames or []))
        return {
            'ok': False,
            'is_live': False,
            'score': 0.0,
            'labels': [],
            'error': 'Anti-spoof pending (Phase 6).',
        }
