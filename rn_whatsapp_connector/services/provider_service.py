# -*- coding: utf-8 -*-
"""Provider abstraction and registry."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnWhatsappProviderService(models.AbstractModel):
    """Resolve provider adapters and expose a single send entry point."""

    _name = 'rn.whatsapp.provider.service'
    _description = 'WhatsApp Provider Service'

    PROVIDER_REGISTRY = {
        'meta_cloud': 'rn.whatsapp.provider.meta',
        'twilio': 'rn.whatsapp.provider.twilio',
        'dialog360': 'rn.whatsapp.provider.dialog360',
        'gupshup': 'rn.whatsapp.provider.gupshup',
        'interakt': 'rn.whatsapp.provider.interakt',
        # Legacy aliases map to meta simulation until dedicated adapters land
        'chat_api': 'rn.whatsapp.provider.meta',
        'ultramsg': 'rn.whatsapp.provider.meta',
        'green_api': 'rn.whatsapp.provider.meta',
    }

    def get_provider(self, account):
        account.ensure_one()
        model_name = self.PROVIDER_REGISTRY.get(account.provider)
        if not model_name:
            return self.env['rn.whatsapp.provider.base']
        return self.env[model_name]

    def test_connection(self, account):
        account.ensure_one()
        provider = self.get_provider(account)
        return provider.test_connection(account)

    def send_message(self, message):
        message.ensure_one()
        account = message.account_id
        provider = self.get_provider(account)
        if message.message_type == 'template' and message.template_id:
            variables = self.env['rn.whatsapp.template.service'].parse_vars_json(message.template_vars)
            return provider.send_template(
                account,
                message.phone,
                message.template_id,
                variables=variables,
            )
        body = message.body
        if message.template_id and not body:
            variables = self.env['rn.whatsapp.template.service'].parse_vars_json(message.template_vars)
            body = self.env['rn.whatsapp.template.service'].render(message.template_id, variables)
        return provider.send_text(account, message.phone, body or '')
