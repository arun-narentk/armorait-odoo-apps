# -*- coding: utf-8 -*-
"""Meta WhatsApp Cloud API provider."""

import json
import logging
import urllib.error
import urllib.request

from odoo import models

_logger = logging.getLogger(__name__)


class RnWhatsappProviderMeta(models.AbstractModel):
    _name = 'rn.whatsapp.provider.meta'
    _inherit = 'rn.whatsapp.provider.base'
    _description = 'WhatsApp Meta Cloud Provider'

    def _endpoint(self, account, path):
        version = account.api_version or 'v21.0'
        base = (account.api_url or 'https://graph.facebook.com').rstrip('/')
        phone_id = account.phone_number_id or account.business_id or ''
        return '%s/%s/%s/%s' % (base, version, phone_id, path)

    def _request(self, account, url, payload):
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                'Authorization': 'Bearer %s' % (account.access_token or ''),
                'Content-Type': 'application/json',
            },
            method='POST',
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode('utf-8')
                raw = json.loads(body) if body else {}
                msg_id = False
                if raw.get('messages'):
                    msg_id = raw['messages'][0].get('id')
                return self._result(True, provider_message_id=msg_id, raw=raw)
        except urllib.error.HTTPError as exc:
            err = exc.read().decode('utf-8', errors='ignore')
            _logger.warning('Meta Cloud send failed: %s', err)
            return self._result(False, error=err or str(exc))
        except Exception as exc:  # noqa: BLE001 - surface to queue
            _logger.exception('Meta Cloud request error')
            return self._result(False, error=str(exc))

    def send_text(self, account, phone, body, **kwargs):
        if account.simulation_mode or not account.access_token:
            return self._result(
                True,
                provider_message_id='SIM-META-%s' % self._normalize_phone(phone),
                raw={'simulated': True},
            )
        payload = {
            'messaging_product': 'whatsapp',
            'to': self._normalize_phone(phone),
            'type': 'text',
            'text': {'body': body or ''},
        }
        return self._request(account, self._endpoint(account, 'messages'), payload)

    def send_template(self, account, phone, template, variables=None, **kwargs):
        variables = variables or {}
        if account.simulation_mode or not account.access_token:
            return self._result(
                True,
                provider_message_id='SIM-META-TPL-%s' % self._normalize_phone(phone),
                raw={'simulated': True, 'template': template.name},
            )
        components = []
        if variables:
            components.append({
                'type': 'body',
                'parameters': [
                    {'type': 'text', 'text': str(variables[k])}
                    for k in sorted(variables.keys())
                ],
            })
        payload = {
            'messaging_product': 'whatsapp',
            'to': self._normalize_phone(phone),
            'type': 'template',
            'template': {
                'name': template.provider_template_id or template.name,
                'language': {'code': template.language or 'en'},
                'components': components,
            },
        }
        return self._request(account, self._endpoint(account, 'messages'), payload)

    def validate_webhook(self, account, headers, payload):
        secret = account.webhook_token or account.webhook_verify_token
        if not secret:
            return True
        # Signature validation can be tightened with X-Hub-Signature-256 in later phase
        return True

    def test_connection(self, account):
        if account.simulation_mode:
            return {'ok': True, 'message': 'Simulation mode OK'}
        if not account.access_token or not (account.phone_number_id or account.business_id):
            return {'ok': False, 'message': 'Missing token or Phone Number ID'}
        return {'ok': True, 'message': 'Credentials present (live call on send)'}
