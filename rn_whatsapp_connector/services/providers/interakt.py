# -*- coding: utf-8 -*-
"""Interakt WhatsApp provider adapter."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnWhatsappProviderInterakt(models.AbstractModel):
    _name = 'rn.whatsapp.provider.interakt'
    _inherit = 'rn.whatsapp.provider.base'
    _description = 'WhatsApp Interakt Provider'

    def send_text(self, account, phone, body, **kwargs):
        _logger.info('Interakt send_text to %s (sim=%s)', phone, account.simulation_mode)
        return self._result(
            True,
            provider_message_id='SIM-INTERAKT-%s' % self._normalize_phone(phone),
            raw={'provider': 'interakt', 'simulated': True},
        )

    def send_template(self, account, phone, template, variables=None, **kwargs):
        return self._result(
            True,
            provider_message_id='SIM-INTERAKT-TPL-%s' % self._normalize_phone(phone),
            raw={'provider': 'interakt', 'template': template.name, 'simulated': True},
        )

    def test_connection(self, account):
        return {'ok': True, 'message': 'Interakt adapter ready (simulation / Phase 1)'}
