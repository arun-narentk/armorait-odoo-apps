# -*- coding: utf-8 -*-
"""Backend dashboard JSON."""

from odoo import http
from odoo.http import request


class RnAiDocumentController(http.Controller):

    @http.route('/rn_ai_document/dashboard/data', type='json', auth='user')
    def dashboard_data(self):
        return request.env['rn.ai.document.dashboard.service'].get_dashboard_data()
