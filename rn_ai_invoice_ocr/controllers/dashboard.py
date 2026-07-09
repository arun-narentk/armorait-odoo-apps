# -*- coding: utf-8 -*-
"""Dashboard JSON route."""

import json

from odoo import http
from odoo.http import request


class RnAiInvoiceOcrDashboardController(http.Controller):

    @http.route('/rn_ai_invoice_ocr/dashboard/data', type='http', auth='user', methods=['GET'])
    def dashboard_data(self):
        payload = request.env['rn.ai.invoice.ocr.dashboard.service'].get_dashboard_data()
        return request.make_response(
            json.dumps(payload),
            headers=[('Content-Type', 'application/json')],
        )
