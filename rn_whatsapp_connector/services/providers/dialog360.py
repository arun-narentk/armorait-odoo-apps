# -*- coding: utf-8 -*-
"""360Dialog WhatsApp provider adapter."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnWhatsappProviderDialog360(models.AbstractModel):
    _name = 'rn.whatsapp.provider.dialog360'
    _inherit = 'rn.whatsapp.provider.base'
    _description = 'WhatsApp 360Dialog Provider'

    def send_text(self, account, phone, body, **kwargs):
        _logger.info('360Dialog send_text to %s (sim=%s)', phone, account.simulation_mode)
        return self._result(
            True,
            provider_message_id='SIM-DIALOG360-%s' % self._normalize_phone(phone),
            raw={'provider': 'dialog360', 'simulated': True},
        )

    def send_template(self, account, phone, template, variables=None, **kwargs):
        return self._result(
            True,
            provider_message_id='SIM-DIALOG360-TPL-%s' % self._normalize_phone(phone),
            raw={'provider': 'dialog360', 'template': template.name, 'simulated': True},
        )

    def test_connection(self, account):
        return {'ok': True, 'message': '360Dialog adapter ready (simulation / Phase 1)'}
