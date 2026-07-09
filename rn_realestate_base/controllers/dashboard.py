# -*- coding: utf-8 -*-
"""Dashboard JSON route."""

import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class RnRealestateDashboardController(http.Controller):

    @http.route('/rn_realestate_base/dashboard/data', type='http', auth='user', methods=['GET'])
    def dashboard_data(self):
        payload = request.env['rn.realestate.dashboard.service'].get_dashboard_data()
        return request.make_response(
            json.dumps(payload),
            headers=[('Content-Type', 'application/json')],
        )
