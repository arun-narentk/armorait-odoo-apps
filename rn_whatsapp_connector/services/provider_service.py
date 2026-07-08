# -*- coding: utf-8 -*-
"""Provider abstraction and registry."""

from odoo import models


class RnWhatsappProviderService(models.AbstractModel):
    """Resolve provider adapters and expose a single send entry point."""

    _name = 'rn.whatsapp.provider.service'
    _description = 'WhatsApp Provider Service'

    PROVIDER_REGISTRY = {
        'meta_cloud': 'rn.whatsapp.provider.meta',
        'chat_api': 'rn.whatsapp.provider.chat_api',
        'twilio': 'rn.whatsapp.provider.twilio',
        'dialog360': 'rn.whatsapp.provider.dialog360',
        'ultramsg': 'rn.whatsapp.provider.ultramsg',
        'green_api': 'rn.whatsapp.provider.green_api',
    }

    def get_provider(self, account):
        """Return the adapter class name for the account provider."""
        account.ensure_one()
        return self.PROVIDER_REGISTRY.get(account.provider)

    def test_connection(self, account):
        """Run a lightweight health check against the provider."""
        account.ensure_one()
        provider_key = self.get_provider(account)
        if not provider_key:
            return {'ok': False, 'message': 'Unsupported provider.'}
        return {'ok': False, 'message': 'Provider adapter pending (Phase 3).'}
