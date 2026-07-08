# -*- coding: utf-8 -*-
"""Abstract WhatsApp provider interface."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnWhatsappProviderBase(models.AbstractModel):
    """Base adapter. Domain adapters override send / webhook methods."""

    _name = 'rn.whatsapp.provider.base'
    _description = 'WhatsApp Provider Base'

    def send_text(self, account, phone, body, **kwargs):
        raise NotImplementedError

    def send_template(self, account, phone, template, variables=None, **kwargs):
        raise NotImplementedError

    def upload_media(self, account, binary_data, mime_type, filename):
        raise NotImplementedError

    def download_media(self, account, media_id):
        raise NotImplementedError

    def validate_webhook(self, account, headers, payload):
        return True

    def process_status_update(self, account, payload):
        return []

    def test_connection(self, account):
        return {'ok': False, 'message': 'Not implemented'}

    def _normalize_phone(self, phone):
        digits = ''.join(ch for ch in (phone or '') if ch.isdigit())
        return digits

    def _result(self, ok, provider_message_id=None, raw=None, error=None):
        return {
            'ok': bool(ok),
            'provider_message_id': provider_message_id,
            'raw': raw or {},
            'error': error,
        }
