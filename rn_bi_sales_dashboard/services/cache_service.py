# -*- coding: utf-8 -*-
"""Simple in-memory cache keyed by company and period."""

import logging
import time

from odoo import models

_logger = logging.getLogger(__name__)

_CACHE = {}


class RnBiCacheService(models.AbstractModel):
    """TTL cache for dashboard payloads (process-local Phase 1)."""

    _name = 'rn.bi.cache.service'
    _description = 'BI Cache Service'

    def get(self, key):
        """Return cached value when still valid."""
        entry = _CACHE.get(key)
        if not entry:
            return None
        if entry['expires'] < time.time():
            _CACHE.pop(key, None)
            return None
        return entry['value']

    def set(self, key, value, ttl=120):
        """Store value with TTL seconds."""
        _CACHE[key] = {'value': value, 'expires': time.time() + int(ttl or 0)}
        return True

    def clear(self, prefix=None):
        """Clear cache entries."""
        if not prefix:
            _CACHE.clear()
            return True
        for key in list(_CACHE):
            if key.startswith(prefix):
                _CACHE.pop(key, None)
        return True
