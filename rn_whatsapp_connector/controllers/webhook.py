# -*- coding: utf-8 -*-
"""Incoming webhook controllers."""

import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class RnWhatsappWebhookController(http.Controller):
    """Receive provider webhooks and delegate to the webhook service."""

    @http.route(
        '/rn_whatsapp/webhook/<string:provider>',
        type='http',
        auth='public',
        methods=['GET', 'POST'],
        csrf=False,
    )
    def webhook(self, provider, **kwargs):
        """Handle verification (GET) and event delivery (POST)."""
        if request.httprequest.method == 'GET':
            mode = kwargs.get('hub.mode')
            token = kwargs.get('hub.verify_token')
            challenge = kwargs.get('hub.challenge')
            provider_key = 'meta_cloud' if provider in ('meta', 'meta_cloud') else provider
            account = request.env['rn.whatsapp.account'].sudo().search([
                ('provider', '=', provider_key),
                ('active', '=', True),
            ], limit=1)
            expected = account.webhook_verify_token if account else False
            if mode == 'subscribe' and expected and token == expected:
                return request.make_response(challenge or '', headers=[('Content-Type', 'text/plain')])
            return request.make_response('Forbidden', status=403)
        payload = request.httprequest.get_data(as_text=True)
        headers = dict(request.httprequest.headers)
        provider_key = 'meta_cloud' if provider in ('meta', 'meta_cloud') else provider
        request.env['rn.whatsapp.webhook.service'].sudo().process_payload(
            provider_key, headers, payload
        )
        return request.make_json_response({'status': 'received'})


class RnWhatsappApiController(http.Controller):

    @http.route('/rn_whatsapp/health', type='http', auth='public', methods=['GET'], csrf=False)
    def health(self):
        return request.make_json_response({'ok': True, 'module': 'rn_whatsapp_connector'})

    @http.route('/api/rn_whatsapp/v1/dashboard', type='json', auth='user')
    def api_dashboard(self):
        return {'ok': True, 'data': request.env['rn.whatsapp.dashboard.service'].get_dashboard_data()}
