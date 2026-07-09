# -*- coding: utf-8 -*-
"""Health and JSON API stubs."""

from odoo import http
from odoo.http import request


class RnAiDocumentApiController(http.Controller):

    @http.route('/rn_ai_document/health', type='http', auth='public', methods=['GET'], csrf=False)
    def health(self):
        return request.make_json_response({'ok': True, 'module': 'rn_ai_document_generator'})

    @http.route('/api/rn_ai_document/v1/dashboard', type='json', auth='user')
    def api_dashboard(self):
        return {'ok': True, 'data': request.env['rn.ai.document.dashboard.service'].get_dashboard_data()}
