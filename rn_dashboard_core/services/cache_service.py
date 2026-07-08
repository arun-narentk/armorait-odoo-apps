# -*- coding: utf-8 -*-
"""Simple in-memory style cache backed by ir.config_parameter JSON stubs."""

import json
import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnDashboardCacheService(models.AbstractModel):
    """TTL cache helpers for expensive dashboard payloads."""

    _name = 'rn.dashboard.cache.service'
    _description = 'Dashboard Cache Service'

    def _param_key(self, key):
        return 'rn_dashboard_core.cache.%s' % key

    def get(self, key):
        ICP = self.env['ir.config_parameter'].sudo()
        raw = ICP.get_param(self._param_key(key))
        if not raw:
            return False
        try:
            payload = json.loads(raw)
        except (TypeError, ValueError):
            return False
        expires = payload.get('expires')
        if not expires:
            return False
        if fields.Datetime.from_string(expires) < fields.Datetime.now():
            return False
        return payload.get('data')

    def set(self, key, data, ttl_seconds=60):
        expires = fields.Datetime.now() + timedelta(seconds=max(1, int(ttl_seconds or 60)))
        payload = {
            'expires': fields.Datetime.to_string(expires),
            'data': data,
        }
        self.env['ir.config_parameter'].sudo().set_param(
            self._param_key(key),
            json.dumps(payload, default=str),
        )
        return True

    def clear_prefix(self, prefix='rn_dashboard_core.cache.'):
        params = self.env['ir.config_parameter'].sudo().search([
            ('key', 'like', prefix + '%'),
        ])
        params.unlink()
        _logger.info('Cleared %s dashboard cache keys', len(params))
        return True
