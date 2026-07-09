# -*- coding: utf-8 -*-
"""HTTP client wrapper for provider API calls."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnWhatsappApiService(models.AbstractModel):
    """Low-level HTTP client with timeout and logging hooks."""

    _name = 'rn.whatsapp.api.service'
    _description = 'WhatsApp API Service'

    def request(self, method, url, headers=None, payload=None, timeout=30):
        """Execute an HTTP request and return a normalized response dict."""
        # Phase 3: implement requests/urllib with retry and redacted logging.
        _logger.debug('WhatsApp API %s %s (payload omitted)', method, url)
        return {
            'ok': False,
            'status_code': 0,
            'json': {},
            'text': '',
            'error': 'API client not implemented yet (Phase 3).',
        }
