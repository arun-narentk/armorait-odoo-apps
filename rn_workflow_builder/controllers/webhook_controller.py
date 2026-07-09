# -*- coding: utf-8 -*-
"""Public webhook endpoint for workflow triggers."""

import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class RnWorkflowWebhookController(http.Controller):

    @http.route('/rn_workflow/webhook/<string:token>', type='json', auth='public', methods=['POST'], csrf=False)
    def workflow_webhook(self, token, **kwargs):
        try:
            payload = request.jsonrequest or {}
        except Exception:
            payload = kwargs
        run_id = request.env['rn.workflow.trigger.service'].sudo().dispatch_webhook(token, payload)
        if not run_id:
            return {'status': 'error', 'message': 'Workflow not found or inactive'}
        return {'status': 'ok', 'run_id': run_id}

    @http.route('/rn_workflow/webhook/<string:token>', type='http', auth='public', methods=['GET'], csrf=False)
    def workflow_webhook_health(self, token, **kwargs):
        workflow = request.env['rn.workflow'].sudo().search([
            ('webhook_token', '=', token),
            ('trigger_type', '=', 'on_webhook'),
        ], limit=1)
        body = json.dumps({
            'status': 'ok' if workflow else 'not_found',
            'workflow': workflow.name if workflow else None,
        })
        return request.make_response(body, headers=[('Content-Type', 'application/json')])
