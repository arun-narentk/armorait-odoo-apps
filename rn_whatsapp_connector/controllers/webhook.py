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
            # Phase 8: Meta verify token handshake.
            challenge = kwargs.get('hub.challenge')
            return request.make_response(challenge or '', headers=[('Content-Type', 'text/plain')])
        payload = request.httprequest.get_data(as_text=True)
        headers = dict(request.httprequest.headers)
        request.env['rn.whatsapp.webhook.service'].sudo().process_payload(
            provider, headers, payload
        )
        return request.make_json_response({'status': 'received'})
