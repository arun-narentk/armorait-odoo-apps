# -*- coding: utf-8 -*-
"""Twilio WhatsApp provider adapter."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnWhatsappProviderTwilio(models.AbstractModel):
    _name = 'rn.whatsapp.provider.twilio'
    _inherit = 'rn.whatsapp.provider.base'
    _description = 'WhatsApp Twilio Provider'

    def send_text(self, account, phone, body, **kwargs):
        _logger.info('Twilio send_text to %s (sim=%s)', phone, account.simulation_mode)
        return self._result(
            True,
            provider_message_id='SIM-TWILIO-%s' % self._normalize_phone(phone),
            raw={'provider': 'twilio', 'simulated': True},
        )

    def send_template(self, account, phone, template, variables=None, **kwargs):
        return self._result(
            True,
            provider_message_id='SIM-TWILIO-TPL-%s' % self._normalize_phone(phone),
            raw={'provider': 'twilio', 'template': template.name, 'simulated': True},
        )

    def test_connection(self, account):
        return {'ok': True, 'message': 'Twilio adapter ready (simulation / Phase 1)'}
