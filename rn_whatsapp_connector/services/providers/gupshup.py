# -*- coding: utf-8 -*-
"""Gupshup WhatsApp provider adapter."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnWhatsappProviderGupshup(models.AbstractModel):
    _name = 'rn.whatsapp.provider.gupshup'
    _inherit = 'rn.whatsapp.provider.base'
    _description = 'WhatsApp Gupshup Provider'

    def send_text(self, account, phone, body, **kwargs):
        _logger.info('Gupshup send_text to %s (sim=%s)', phone, account.simulation_mode)
        return self._result(
            True,
            provider_message_id='SIM-GUPSHUP-%s' % self._normalize_phone(phone),
            raw={'provider': 'gupshup', 'simulated': True},
        )

    def send_template(self, account, phone, template, variables=None, **kwargs):
        return self._result(
            True,
            provider_message_id='SIM-GUPSHUP-TPL-%s' % self._normalize_phone(phone),
            raw={'provider': 'gupshup', 'template': template.name, 'simulated': True},
        )

    def test_connection(self, account):
        return {'ok': True, 'message': 'Gupshup adapter ready (simulation / Phase 1)'}
