# -*- coding: utf-8 -*-
"""Dashboard JSON route."""

import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class RnAiSiteDashboardController(http.Controller):

    @http.route('/rn_ai_site_base/dashboard/data', type='http', auth='user', methods=['GET'])
    def dashboard_data(self):
        payload = request.env['rn.ai.site.dashboard.service'].get_dashboard_data()
        return request.make_response(
            json.dumps(payload),
            headers=[('Content-Type', 'application/json')],
        )
