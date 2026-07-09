# -*- coding: utf-8 -*-
"""Public webhook endpoints for messaging providers."""

import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class RnMessagingWebhookController(http.Controller):

    @http.route(
        '/rn_messaging/webhook/<int:connector_id>',
        type='http',
        auth='public',
        methods=['GET', 'POST'],
        csrf=False,
    )
    def webhook(self, connector_id, **kwargs):
        connector = request.env['rn.messaging.connector'].sudo().browse(connector_id).exists()
        if not connector:
            return request.make_response('Not Found', status=404)
        if request.httprequest.method == 'GET':
            challenge = kwargs.get('hub.challenge') or kwargs.get('challenge')
            token = kwargs.get('hub.verify_token') or kwargs.get('verify_token')
            service = request.env['rn.messaging.webhook.service'].sudo()
            if service.verify_token(connector, token):
                return request.make_response(challenge or '', status=200)
            return request.make_response('Forbidden', status=403)
        try:
            payload = request.get_json_data() or {}
        except Exception:
            payload = {}
        if not payload and request.httprequest.data:
            try:
                payload = json.loads(request.httprequest.data.decode('utf-8'))
            except json.JSONDecodeError:
                payload = {}
        request.env['rn.messaging.webhook.service'].sudo().ingest_payload(connector, payload)
        return request.make_response('OK', status=200)
